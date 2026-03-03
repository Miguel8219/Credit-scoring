import csv
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
RAW_FILE = BASE_DIR / "raw" / "german_credit_data.csv-2.xls"
DB_FILE = BASE_DIR / "database" / "credit_scoring.db"


def clean_text(value):
	if value is None:
		return None
	value = value.strip()
	if value == "" or value.upper() == "NA":
		return None
	return value


def clean_int(value):
	value = clean_text(value)
	if value is None:
		return None
	return int(value)


def create_tables(conn):
	conn.executescript(
		"""
		PRAGMA foreign_keys = ON;

		CREATE TABLE IF NOT EXISTS clients (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			original_id INTEGER NOT NULL UNIQUE,
			age INTEGER,
			sex TEXT,
			job INTEGER,
			housing TEXT,
			saving_accounts TEXT,
			checking_account TEXT
		);

		CREATE TABLE IF NOT EXISTS loans (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			client_id INTEGER NOT NULL,
			credit_amount INTEGER,
			duration INTEGER,
			purpose TEXT,
			risk TEXT,
			FOREIGN KEY (client_id) REFERENCES clients (id)
		);
		"""
	)


def build_database():
	DB_FILE.parent.mkdir(parents=True, exist_ok=True)
	conn = sqlite3.connect(DB_FILE)
	create_tables(conn)

	conn.execute("DELETE FROM loans")
	conn.execute("DELETE FROM clients")

	with RAW_FILE.open("r", encoding="utf-8", newline="") as csv_file:
		reader = csv.DictReader(csv_file)
		for row in reader:
			original_id = clean_int(row.get(""))
			if original_id is None:
				continue

			conn.execute(
				"""
				INSERT INTO clients (
					original_id, age, sex, job, housing, saving_accounts, checking_account
				)
				VALUES (?, ?, ?, ?, ?, ?, ?)
				""",
				(
					original_id,
					clean_int(row.get("Age")),
					clean_text(row.get("Sex")),
					clean_int(row.get("Job")),
					clean_text(row.get("Housing")),
					clean_text(row.get("Saving accounts")),
					clean_text(row.get("Checking account")),
				),
			)

			client_id = conn.execute(
				"SELECT id FROM clients WHERE original_id = ?",
				(original_id,),
			).fetchone()[0]

			conn.execute(
				"""
				INSERT INTO loans (client_id, credit_amount, duration, purpose, risk)
				VALUES (?, ?, ?, ?, ?)
				""",
				(
					client_id,
					clean_int(row.get("Credit amount")),
					clean_int(row.get("Duration")),
					clean_text(row.get("Purpose")),
					clean_text(row.get("Risk")),
				),
			)

	conn.commit()

	clients_count = conn.execute("SELECT COUNT(*) FROM clients").fetchone()[0]
	loans_count = conn.execute("SELECT COUNT(*) FROM loans").fetchone()[0]
	conn.close()

	print("Banco criado com sucesso")
	print("Arquivo:", DB_FILE)
	print("Clientes:", clients_count)
	print("Emprestimos:", loans_count)


if __name__ == "__main__":
	build_database()
