import sqlite3
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self):
        self.con = sqlite3.connect(
            "ylerobo.db", detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        self.con.row_factory = sqlite3.Row

    def init(self, force: bool):
        cur = self.con.cursor()
        if force:
            logger.warning("Re-initializing database.")
            cur.execute("""DROP TABLE IF EXISTS AreenaSeries""")
            cur.execute("""DROP TABLE IF EXISTS AreenaEpisode""")

        try:
            cur.execute(
                """
                CREATE TABLE AreenaSeries (
                    program_id VARCHAR(32) NOT NULL,
                    webpage TINYTEXT,
                    title TEXT,
                    freq TINYTEXT,
                    last_check TIMESTAMP NULL,
                    PRIMARY KEY (program_id)
                )"""
            )

            cur.execute(
                """
                CREATE TABLE AreenaEpisode (
                    program_id VARCHAR(32) NOT NULL,
                    series_program_id VARCHAR(32) NOT NULL,
                    webpage TINYTEXT NOT NULL,
                    title TINYTEXT NOT NULL,
                    description TEXT NOT NULL,
                    filename TINYTEXT NOT NULL,
                    download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (program_id)
                )"""
            )
        except sqlite3.OperationalError as e:
            self.con.rollback()
            logger.error(f'SQLite: "{str(e)}"')
            logger.error("Use --force to drop existing tables.")
            return False

        self.con.commit()
        logger.debug("Initialized")
        return True

    def add(self, program_id: str, url: str, title: str, freq: str):
        cur = self.con.cursor()
        try:
            cur.execute(
                """
                INSERT INTO AreenaSeries
                    (program_id, webpage, title, freq, last_check)
                VALUES
                    (?,?,?,?,NULL)
                """,
                (program_id, url, title, freq),
            )
        except sqlite3.IntegrityError:
            logger.error("Program already exists.")
            return False
        self.con.commit()
        logger.debug(f"Added {program_id}")
        return True

    def remove(self, program_id: str):
        cur = self.con.cursor()
        cur.execute("DELETE FROM AreenaSeries WHERE program_id=?", (program_id,))
        self.con.commit()
        logger.debug(f"Deleted {program_id}")

    def update(self, program_id: str):
        cur = self.con.cursor()
        cur.execute(
            """
            UPDATE AreenaSeries
                SET last_check=datetime('now')
                WHERE program_id=?
            """,
            (program_id,),
        )
        self.con.commit()
        logger.debug(f"Updated {program_id}")

    def list(self):
        cur = self.con.cursor()
        cur.execute(
            """
            SELECT program_id, webpage, title, freq, last_check,
                   julianday('now')-julianday(last_check) as days_since_check
                FROM AreenaSeries
            """
        )
        for row in cur:
            yield row

    def episode_list(self, program_id):
        cur = self.con.cursor()
        cur.execute(
            """
            SELECT program_id, webpage, title, download_date
                FROM AreenaEpisode
                WHERE series_program_id=?
            """,
            (program_id,),
        )
        for row in cur:
            yield row

    def episode_exists(self, program_id):
        cur = self.con.cursor()
        cur.execute(
            "SELECT program_id FROM AreenaEpisode WHERE program_id=?", (program_id,)
        )
        row = cur.fetchone()
        exists = row is not None
        logger.debug(f"Episode {program_id} exists: {exists}")
        return exists

    def episode_add(self, series_program_id, episode):
        cur = self.con.cursor()
        cur.execute(
            """
            INSERT INTO AreenaEpisode (
                program_id, series_program_id, webpage, title, description, filename
                ) VALUES (
                ?, ?, ?, ?, ?, ?
                )
            """,
            (
                episode["program_id"],
                series_program_id,
                episode["webpage"],
                episode["title"],
                episode["description"],
                episode["filename"],
            ),
        )
        self.con.commit()
        logger.debug(
            f"Added {episode['program_id']} {episode['title']} {episode['filename']}"
        )
