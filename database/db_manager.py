# database/db_manager.py - مدير قاعدة البيانات المتقدم

import sqlite3
import json
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from contextlib import asynccontextmanager
import aiosqlite
import os

from core.config import config, paths
from utils.logger import logger_manager
from utils.helpers import safe_json_dumps, safe_json_loads

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    مدير قاعدة البيانات المتقدم
    يدعم العمليات غير المتزامنة والتخزين المؤقت والنسخ الاحتياطي
    """
    
    def __init__(self):
        self.db_path = paths.DATABASE_FILE
        self.pool = None
        self.connection = None
        self.cache = {}
        self.cache_timeout = 300  # 5 دقائق
        self.logger = logger_manager.get_logger('database')
        
        # التأكد من وجود المجلد
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    async def initialize(self):
        """تهيئة قاعدة البيانات وإنشاء الجداول"""
        try:
            async with aiosqlite.connect(self.db_path) as db:
                # تفعيل المفاتيح الخارجية
                await db.execute("PRAGMA foreign_keys = ON")
                
                # تفعيل وضع WAL للسرعة
                await db.execute("PRAGMA journal_mode = WAL")
                
                # إنشاء الجداول
                await self._create_tables(db)
                
                # تطبيق تحديثات مخطط قاعدة البيانات (migrations)
                await self._run_migrations(db)

                # التحقق من وجود البيانات الأساسية
                await self._seed_data(db)
                
                await db.commit()
                
            self.logger.info(f"✅ قاعدة البيانات جاهزة: {self.db_path}")
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تهيئة قاعدة البيانات: {e}")
            raise
    
    async def _create_tables(self, db: aiosqlite.Connection):
        """إنشاء جداول قاعدة البيانات"""
        
        # جدول اللاعبين
        await db.execute('''
            CREATE TABLE IF NOT EXISTS players (
                user_id INTEGER PRIMARY KEY,
                username TEXT NOT NULL,
                
                -- التقدم في العوالم
                current_world TEXT DEFAULT 'fantasy',
                fantasy_part TEXT DEFAULT 'FANTASY_01',
                retro_part TEXT DEFAULT NULL,
                future_part TEXT DEFAULT NULL,
                alternate_part TEXT DEFAULT NULL,
                
                -- النهايات
                fantasy_ending TEXT DEFAULT NULL,
                retro_ending TEXT DEFAULT NULL,
                future_ending TEXT DEFAULT NULL,
                alternate_ending TEXT DEFAULT NULL,
                
                -- المتغيرات الأساسية
                shards INTEGER DEFAULT 0,
                corruption INTEGER DEFAULT 0,
                mystery INTEGER DEFAULT 0,
                reputation INTEGER DEFAULT 0,
                alignment TEXT DEFAULT 'Gray',
                world_stability INTEGER DEFAULT 100,
                
                -- متغيرات خاصة بكل عالم
                fantasy_power INTEGER DEFAULT 0,
                memories INTEGER DEFAULT 0,
                tech_level INTEGER DEFAULT 0,
                identity INTEGER DEFAULT 0,
                
                -- متغيرات العلاقات
                trust_aren INTEGER DEFAULT 0,
                
                -- نظام التطور
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                knowledge_path INTEGER DEFAULT 0,
                
                -- معلومات إضافية
                location TEXT DEFAULT 'أنقاض',
                play_time INTEGER DEFAULT 0,
                choices_count INTEGER DEFAULT 0,
                
                -- تواريخ
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_active TEXT DEFAULT CURRENT_TIMESTAMP,
                last_daily TEXT DEFAULT NULL,
                daily_streak INTEGER DEFAULT 0,
                last_save TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الإنجازات
        await db.execute('''
            CREATE TABLE IF NOT EXISTS achievements (
                user_id INTEGER,
                achievement_id TEXT,
                world TEXT,
                unlocked_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, achievement_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول المخزون
        await db.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                user_id INTEGER,
                item_id TEXT,
                item_name TEXT,
                item_emoji TEXT,
                quantity INTEGER DEFAULT 1,
                acquired_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, item_id),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول العلامات (Flags)
        await db.execute('''
            CREATE TABLE IF NOT EXISTS flags (
                user_id INTEGER,
                flag_name TEXT,
                flag_value INTEGER DEFAULT 1,
                set_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (user_id, flag_name),
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول تاريخ القرارات
        await db.execute('''
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                world TEXT,
                part_id TEXT,
                choice_text TEXT,
                effects TEXT,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول إحصائيات العالم
        await db.execute('''
            CREATE TABLE IF NOT EXISTS world_stats (
                world_id TEXT PRIMARY KEY,
                total_players INTEGER DEFAULT 0,
                completed_players INTEGER DEFAULT 0,
                popular_choices TEXT DEFAULT '{}',
                average_corruption REAL DEFAULT 0,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الجلسات النشطة
        await db.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                user_id INTEGER PRIMARY KEY,
                current_part TEXT,
                session_start TEXT DEFAULT CURRENT_TIMESTAMP,
                last_interaction TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES players(user_id) ON DELETE CASCADE
            )
        ''')
        
        # جدول النسخ الاحتياطي
        await db.execute('''
            CREATE TABLE IF NOT EXISTS backups (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                backup_path TEXT,
                backup_size INTEGER,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول تعيين قنوات العوالم لكل سيرفر
        await db.execute('''
            CREATE TABLE IF NOT EXISTS guild_world_channels (
                guild_id INTEGER,
                world_id TEXT,
                channel_id INTEGER,
                set_by INTEGER,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (guild_id, world_id)
            )
        ''')

        # إنشاء الفهارس للسرعة
        await db.execute('CREATE INDEX IF NOT EXISTS idx_players_world ON players(current_world)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_players_active ON players(last_active)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_history_user ON history(user_id)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_history_timestamp ON history(timestamp)')
        await db.execute('CREATE INDEX IF NOT EXISTS idx_guild_world_channels ON guild_world_channels(guild_id, world_id)')
        
        self.logger.info("✅ تم إنشاء جميع الجداول")
    

    async def _run_migrations(self, db: aiosqlite.Connection):
        """تطبيق ترقيات آمنة على الجداول القديمة"""
        cursor = await db.execute("PRAGMA table_info(players)")
        columns = {row[1] for row in await cursor.fetchall()}

        if "identity" not in columns:
            await db.execute("ALTER TABLE players ADD COLUMN identity INTEGER DEFAULT 0")
            self.logger.info("✅ Migration: تمت إضافة العمود identity")

        if "daily_streak" not in columns:
            await db.execute("ALTER TABLE players ADD COLUMN daily_streak INTEGER DEFAULT 0")
            self.logger.info("✅ Migration: تمت إضافة العمود daily_streak")

        # توحيد معرفات العوالم القديمة (past/alt) إلى القيم القياسية (retro/alternate)
        await db.execute("UPDATE players SET current_world = 'retro' WHERE current_world = 'past'")
        await db.execute("UPDATE players SET current_world = 'alternate' WHERE current_world = 'alt'")

        # world_stats: تجنب تعارض المفتاح الأساسي عند وجود سجلين past + retro
        await db.execute("DELETE FROM world_stats WHERE world_id = 'past' AND EXISTS (SELECT 1 FROM world_stats WHERE world_id = 'retro')")
        await db.execute("DELETE FROM world_stats WHERE world_id = 'alt' AND EXISTS (SELECT 1 FROM world_stats WHERE world_id = 'alternate')")
        await db.execute("UPDATE world_stats SET world_id = 'retro' WHERE world_id = 'past'")
        await db.execute("UPDATE world_stats SET world_id = 'alternate' WHERE world_id = 'alt'")

        # guild_world_channels: تجنب تعارض (guild_id, world_id)
        await db.execute('''
            DELETE FROM guild_world_channels
            WHERE world_id = 'past'
              AND EXISTS (
                  SELECT 1 FROM guild_world_channels g2
                  WHERE g2.guild_id = guild_world_channels.guild_id
                    AND g2.world_id = 'retro'
              )
        ''')
        await db.execute('''
            DELETE FROM guild_world_channels
            WHERE world_id = 'alt'
              AND EXISTS (
                  SELECT 1 FROM guild_world_channels g2
                  WHERE g2.guild_id = guild_world_channels.guild_id
                    AND g2.world_id = 'alternate'
              )
        ''')
        await db.execute("UPDATE guild_world_channels SET world_id = 'retro' WHERE world_id = 'past'")
        await db.execute("UPDATE guild_world_channels SET world_id = 'alternate' WHERE world_id = 'alt'")

    async def _seed_data(self, db: aiosqlite.Connection):
        """إضافة بيانات أولية إذا كانت قاعدة البيانات فارغة"""
        
        # التحقق من وجود إحصائيات العوالم
        cursor = await db.execute("SELECT COUNT(*) FROM world_stats")
        count = (await cursor.fetchone())[0]
        
        if count == 0:
            # إضافة إحصائيات أولية للعوالم
            worlds = ["fantasy", "retro", "future", "alternate"]
            for world in worlds:
                await db.execute(
                    "INSERT INTO world_stats (world_id) VALUES (?)",
                    (world,)
                )
            self.logger.info("✅ تم إضافة البيانات الأولية")
    
    @asynccontextmanager
    async def get_connection(self):
        """الحصول على اتصال بقاعدة البيانات (Context Manager)"""
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("PRAGMA foreign_keys = ON")
            yield db
    
    async def execute(self, query: str, params: tuple = ()) -> Optional[int]:
        """تنفيذ استعلام (إدراج، تحديث، حذف)"""
        try:
            async with self.get_connection() as db:
                cursor = await db.execute(query, params)
                await db.commit()
                return cursor.lastrowid
        except Exception as e:
            self.logger.error(f"❌ خطأ في تنفيذ الاستعلام: {e}\n{query}\n{params}")
            raise
    
    async def fetch_one(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """جلب صف واحد"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                row = await cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            self.logger.error(f"❌ خطأ في جلب البيانات: {e}")
            return None
    
    async def fetch_all(self, query: str, params: tuple = ()) -> List[Dict]:
        """جلب كل الصفوف"""
        try:
            async with self.get_connection() as db:
                db.row_factory = aiosqlite.Row
                cursor = await db.execute(query, params)
                rows = await cursor.fetchall()
                return [dict(row) for row in rows]
        except Exception as e:
            self.logger.error(f"❌ خطأ في جلب البيانات: {e}")
            return []
    
    # ============================================
    # دوال اللاعبين
    # ============================================
    
    async def get_player(self, user_id: int) -> Optional[Dict]:
        """الحصول على بيانات لاعب"""
        # التحقق من التخزين المؤقت
        cache_key = f"player_{user_id}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.cache_timeout:
                return data
        
        query = "SELECT * FROM players WHERE user_id = ?"
        player = await self.fetch_one(query, (user_id,))
        
        # تحديث آخر نشاط
        if player:
            await self.update_player(user_id, {"last_active": datetime.now().isoformat()})
            self.cache[cache_key] = (datetime.now(), player)
        
        return player
    
    async def create_player(self, user_id: int, username: str) -> bool:
        """إنشاء لاعب جديد"""
        try:
            query = '''
                INSERT INTO players 
                (user_id, username, current_world, fantasy_part, created_at, last_active)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            now = datetime.now().isoformat()
            await self.execute(query, (user_id, username, 'fantasy', 'FANTASY_01', now, now))
            
            # إضافة عناصر بداية
            await self.add_to_inventory(user_id, "potion", "🧪 جرعة نقاء", 3)
            
            # تحديث إحصائيات العالم
            await self.update_world_stats('fantasy', 'new_player')
            
            self.logger.info(f"👤 لاعب جديد: {username} (ID: {user_id})")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إنشاء لاعب: {e}")
            return False
    
    async def update_player(self, user_id: int, updates: Dict) -> bool:
        """تحديث بيانات لاعب"""
        if not updates:
            return False
        
        try:
            set_clause = ", ".join([f"{k} = ?" for k in updates.keys()])
            query = f"UPDATE players SET {set_clause}, last_active = ? WHERE user_id = ?"
            
            params = list(updates.values())
            params.append(datetime.now().isoformat())
            params.append(user_id)
            
            await self.execute(query, tuple(params))
            
            # تحديث التخزين المؤقت
            cache_key = f"player_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث لاعب: {e}")
            return False
    
    async def delete_player(self, user_id: int) -> bool:
        """حذف لاعب نهائياً"""
        try:
            # حذف البيانات المرتبطة (بسبب ON DELETE CASCADE)
            await self.execute("DELETE FROM players WHERE user_id = ?", (user_id,))
            
            # حذف من التخزين المؤقت
            cache_key = f"player_{user_id}"
            if cache_key in self.cache:
                del self.cache[cache_key]
            
            self.logger.info(f"🗑️ تم حذف اللاعب {user_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في حذف لاعب: {e}")
            return False
    
    # ============================================
    # دوال الإنجازات
    # ============================================
    
    async def unlock_achievement(self, user_id: int, achievement_id: str, world: str) -> bool:
        """فتح إنجاز للاعب"""
        try:
            query = '''
                INSERT INTO achievements (user_id, achievement_id, world, unlocked_at)
                VALUES (?, ?, ?, ?)
            '''
            await self.execute(query, (user_id, achievement_id, world, datetime.now().isoformat()))
            
            self.logger.info(f"🏆 إنجاز جديد: {achievement_id} للمستخدم {user_id}")
            return True
            
        except sqlite3.IntegrityError:
            # الإنجاز مفتوح بالفعل
            return False
        except Exception as e:
            self.logger.error(f"❌ خطأ في فتح إنجاز: {e}")
            return False
    
    async def get_achievements(self, user_id: int) -> List[Dict]:
        """الحصول على إنجازات لاعب"""
        query = "SELECT * FROM achievements WHERE user_id = ? ORDER BY unlocked_at DESC"
        return await self.fetch_all(query, (user_id,))
    
    async def has_achievement(self, user_id: int, achievement_id: str) -> bool:
        """التحقق مما إذا كان لدى اللاعب إنجاز معين"""
        query = "SELECT 1 FROM achievements WHERE user_id = ? AND achievement_id = ?"
        result = await self.fetch_one(query, (user_id, achievement_id))
        return result is not None
    
    # ============================================
    # دوال المخزون
    # ============================================
    
    async def add_to_inventory(self, user_id: int, item_id: str, item_name: str, quantity: int = 1) -> bool:
        """إضافة عنصر إلى مخزون لاعب"""
        try:
            # التحقق من وجود العنصر
            query = "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?"
            existing = await self.fetch_one(query, (user_id, item_id))
            
            if existing:
                # تحديث الكمية
                new_qty = existing['quantity'] + quantity
                await self.execute(
                    "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                    (new_qty, user_id, item_id)
                )
            else:
                # إضافة عنصر جديد
                await self.execute(
                    "INSERT INTO inventory (user_id, item_id, item_name, quantity) VALUES (?, ?, ?, ?)",
                    (user_id, item_id, item_name, quantity)
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إضافة عنصر: {e}")
            return False
    
    async def remove_from_inventory(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        """إزالة عنصر من مخزون لاعب"""
        try:
            query = "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?"
            existing = await self.fetch_one(query, (user_id, item_id))
            
            if not existing:
                return False
            
            new_qty = existing['quantity'] - quantity
            
            if new_qty <= 0:
                await self.execute(
                    "DELETE FROM inventory WHERE user_id = ? AND item_id = ?",
                    (user_id, item_id)
                )
            else:
                await self.execute(
                    "UPDATE inventory SET quantity = ? WHERE user_id = ? AND item_id = ?",
                    (new_qty, user_id, item_id)
                )
            
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إزالة عنصر: {e}")
            return False
    
    async def get_inventory(self, user_id: int) -> List[Dict]:
        """الحصول على مخزون لاعب"""
        query = "SELECT * FROM inventory WHERE user_id = ? AND quantity > 0 ORDER BY item_name"
        return await self.fetch_all(query, (user_id,))
    
    async def has_item(self, user_id: int, item_id: str, quantity: int = 1) -> bool:
        """التحقق من امتلاك لاعب لعنصر معين"""
        query = "SELECT quantity FROM inventory WHERE user_id = ? AND item_id = ?"
        result = await self.fetch_one(query, (user_id, item_id))
        return result is not None and result['quantity'] >= quantity
    
    # ============================================
    # دوال العلامات (Flags)
    # ============================================
    
    async def set_flag(self, user_id: int, flag_name: str, value: int = 1) -> bool:
        """تعيين علامة للاعب"""
        try:
            query = '''
                INSERT INTO flags (user_id, flag_name, flag_value, set_at)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id, flag_name) 
                DO UPDATE SET flag_value = excluded.flag_value, set_at = excluded.set_at
            '''
            await self.execute(query, (user_id, flag_name, value, datetime.now().isoformat()))
            return True
        except Exception as e:
            self.logger.error(f"❌ خطأ في تعيين علامة: {e}")
            return False
    
    async def get_flag(self, user_id: int, flag_name: str) -> int:
        """الحصول على قيمة علامة"""
        query = "SELECT flag_value FROM flags WHERE user_id = ? AND flag_name = ?"
        result = await self.fetch_one(query, (user_id, flag_name))
        return result['flag_value'] if result else 0
    
    async def has_flag(self, user_id: int, flag_name: str) -> bool:
        """التحقق من وجود علامة"""
        return await self.get_flag(user_id, flag_name) > 0
    
    # ============================================
    # دوال تاريخ القرارات
    # ============================================
    
    async def add_history(self, user_id: int, world: str, part_id: str, choice_text: str, effects: Dict = None):
        """إضافة قرار إلى التاريخ"""
        try:
            effects_json = safe_json_dumps(effects or {})
            query = '''
                INSERT INTO history (user_id, world, part_id, choice_text, effects, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            '''
            await self.execute(query, (user_id, world, part_id, choice_text, effects_json, datetime.now().isoformat()))
            
            # تحديث عدد القرارات
            await self.execute(
                "UPDATE players SET choices_count = choices_count + 1 WHERE user_id = ?",
                (user_id,)
            )
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إضافة تاريخ: {e}")
    
    async def get_history(self, user_id: int, limit: int = 10) -> List[Dict]:
        """الحصول على تاريخ قرارات لاعب"""
        query = '''
            SELECT * FROM history 
            WHERE user_id = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        rows = await self.fetch_all(query, (user_id, limit))
        
        # تحويل JSON للتأثيرات
        for row in rows:
            if row.get('effects'):
                row['effects'] = safe_json_loads(row['effects'], {})
        
        return rows
    
    # ============================================
    # دوال إحصائيات العالم
    # ============================================
    
    async def update_world_stats(self, world_id: str, action: str):
        """تحديث إحصائيات العالم"""
        try:
            if action == 'new_player':
                await self.execute(
                    "UPDATE world_stats SET total_players = total_players + 1, updated_at = ? WHERE world_id = ?",
                    (datetime.now().isoformat(), world_id)
                )
            elif action == 'complete':
                await self.execute(
                    "UPDATE world_stats SET completed_players = completed_players + 1, updated_at = ? WHERE world_id = ?",
                    (datetime.now().isoformat(), world_id)
                )
        except Exception as e:
            self.logger.error(f"❌ خطأ في تحديث إحصائيات العالم: {e}")
    
    async def get_world_stats(self, world_id: str) -> Dict:
        """الحصول على إحصائيات عالم"""
        query = "SELECT * FROM world_stats WHERE world_id = ?"
        stats = await self.fetch_one(query, (world_id,))
        
        if stats and stats.get('popular_choices'):
            stats['popular_choices'] = safe_json_loads(stats['popular_choices'], {})
        
        return stats or {}
    
    # ============================================
    # دوال الجلسات
    # ============================================
    
    async def create_session(self, user_id: int, current_part: str):
        """إنشاء جلسة للاعب"""
        try:
            query = '''
                INSERT INTO sessions (user_id, current_part, session_start, last_interaction)
                VALUES (?, ?, ?, ?)
                ON CONFLICT(user_id) 
                DO UPDATE SET current_part = excluded.current_part, last_interaction = excluded.last_interaction
            '''
            now = datetime.now().isoformat()
            await self.execute(query, (user_id, current_part, now, now))
        except Exception as e:
            self.logger.error(f"❌ خطأ في إنشاء جلسة: {e}")

    async def save_session(self, user_id: int, current_part: str):
        """توافق عكسي: حفظ/تحديث جلسة اللاعب الحالية"""
        await self.create_session(user_id, current_part)
        
    async def save_session(self, user_id: int, current_part: str):
        """توافق عكسي: حفظ/تحديث جلسة اللاعب الحالية"""
        await self.create_session(user_id, current_part)
    
    async def update_session(self, user_id: int):
        """تحديث آخر تفاعل في الجلسة"""
        await self.execute(
            "UPDATE sessions SET last_interaction = ? WHERE user_id = ?",
            (datetime.now().isoformat(), user_id)
        )
    
    async def get_session(self, user_id: int) -> Optional[Dict]:
        """الحصول على جلسة لاعب"""
        query = "SELECT * FROM sessions WHERE user_id = ?"
        return await self.fetch_one(query, (user_id,))
    
    async def delete_session(self, user_id: int):
        """حذف جلسة لاعب"""
        await self.execute("DELETE FROM sessions WHERE user_id = ?", (user_id,))
    
    async def cleanup_sessions(self, max_age: int = 3600):
        """تنظيف الجلسات القديمة"""
        cutoff = (datetime.now() - timedelta(seconds=max_age)).isoformat()
        await self.execute("DELETE FROM sessions WHERE last_interaction < ?", (cutoff,))
        self.logger.info("🧹 تم تنظيف الجلسات القديمة")

    # ============================================
    # دوال إعدادات السيرفر (قنوات العوالم)
    # ============================================

    async def set_world_channel(self, guild_id: int, world_id: str, channel_id: int, set_by: int) -> bool:
        """تعيين قناة عالم لسيرفر محدد"""
        try:
            query = """
                INSERT INTO guild_world_channels (guild_id, world_id, channel_id, set_by, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(guild_id, world_id)
                DO UPDATE SET channel_id = excluded.channel_id, set_by = excluded.set_by, updated_at = excluded.updated_at
            """
            await self.execute(query, (guild_id, world_id, channel_id, set_by, datetime.now().isoformat()))
            return True
        except Exception as e:
            self.logger.error(f"❌ خطأ في تعيين قناة العالم: {e}")
            return False

    async def get_world_channel(self, guild_id: int, world_id: str) -> Optional[int]:
        """الحصول على قناة عالم لسيرف محدد"""
        row = await self.fetch_one(
            "SELECT channel_id FROM guild_world_channels WHERE guild_id = ? AND world_id = ?",
            (guild_id, world_id)
        )
        return row.get('channel_id') if row else None

    async def get_guild_world_channels(self, guild_id: int) -> Dict[str, int]:
        """الحصول على كل قنوات العوالم لسيرفر محدد"""
        rows = await self.fetch_all(
            "SELECT world_id, channel_id FROM guild_world_channels WHERE guild_id = ?",
            (guild_id,)
        )
        return {row['world_id']: row['channel_id'] for row in rows}

    # ============================================
    # دوال النسخ الاحتياطي
    # ============================================
    
    async def create_backup(self, backup_path: str = None) -> bool:
        """إنشاء نسخة احتياطية"""
        try:
            if not backup_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_path = f"data/backups/backup_{timestamp}.db"
            
            # التأكد من وجود المجلد
            os.makedirs(os.path.dirname(backup_path), exist_ok=True)
            
            # نسخ قاعدة البيانات
            import shutil
            shutil.copy2(self.db_path, backup_path)
            
            # تسجيل النسخة
            size = os.path.getsize(backup_path)
            await self.execute(
                "INSERT INTO backups (backup_path, backup_size) VALUES (?, ?)",
                (backup_path, size)
            )
            
            self.logger.info(f"✅ تم إنشاء نسخة احتياطية: {backup_path} ({size} bytes)")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في إنشاء نسخة احتياطية: {e}")
            return False
    
    async def restore_backup(self, backup_path: str) -> bool:
        """استعادة نسخة احتياطية"""
        try:
            if not os.path.exists(backup_path):
                self.logger.error(f"❌ ملف النسخة غير موجود: {backup_path}")
                return False
            
            # إغلاق الاتصالات الحالية
            await self.close()
            
            # استعادة الملف
            import shutil
            shutil.copy2(backup_path, self.db_path)
            
            # إعادة الاتصال
            await self.initialize()
            
            self.logger.info(f"✅ تم استعادة النسخة: {backup_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ خطأ في استعادة النسخة: {e}")
            return False
    
    # ============================================
    # دوال إحصائية
    # ============================================
    
    async def get_total_players(self) -> int:
        """الحصول على عدد اللاعبين الكلي"""
        result = await self.fetch_one("SELECT COUNT(*) as count FROM players")
        return result['count'] if result else 0

    async def get_users_count(self) -> int:
        """توافق عكسي: نفس get_total_players"""
        return await self.get_total_players()
        
    async def get_active_players(self, minutes: int = 60) -> int:
        """الحصول على عدد اللاعبين النشطين"""
        cutoff = (datetime.now() - timedelta(minutes=minutes)).isoformat()
        result = await self.fetch_one(
            "SELECT COUNT(*) as count FROM players WHERE last_active > ?",
            (cutoff,)
        )
        return result['count'] if result else 0
    
    async def get_total_completions(self) -> int:
        """الحصول على عدد مرات إكمال العوالم"""
        query = '''
            SELECT 
                COUNT(fantasy_ending) as fantasy,
                COUNT(retro_ending) as retro,
                COUNT(future_ending) as future,
                COUNT(alternate_ending) as alternate
            FROM players
        '''
        result = await self.fetch_one(query)
        return sum(result.values()) if result else 0
    
    async def get_total_achievements(self) -> int:
        """الحصول على عدد الإنجازات المفتوحة"""
        result = await self.fetch_one("SELECT COUNT(*) as count FROM achievements")
        return result['count'] if result else 0

    async def get_bot_stats(self) -> Dict[str, int]:
        """إحصائيات عامة للبوت لاستخدامها في شاشة الحالة"""
        total_completions = await self.get_total_completions()
        total_achievements = await self.get_total_achievements()
        return {
            "worlds_completed": total_completions,
            "total_achievements": total_achievements,
        }
        
    # ============================================
    # دوال الصيانة
    # ============================================
    
    async def vacuum(self):
        """تحسين قاعدة البيانات"""
        async with self.get_connection() as db:
            await db.execute("VACUUM")
        self.logger.info("✅ تم تحسين قاعدة البيانات")
    
    async def close(self):
        """إغلاق الاتصالات"""
        self.cache.clear()
        self.logger.info("✅ تم إغلاق قاعدة البيانات")

    async def commit(self):
        """توافق عكسي: لا حاجة للـ commit لأن كل عملية تُحفظ فوراً"""
        return None
        
    async def save_all(self):
        """حفظ كل البيانات (للحفظ التلقائي)"""
        # التخزين المؤقت يتم تلقائياً مع كل عملية
        # هذه الدالة للتأكد فقط
        self.logger.debug("✅ تم حفظ البيانات")
