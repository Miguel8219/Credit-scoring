import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
DB_FILE = BASE_DIR / "database" / "credit_scoring.db"


def run_examples():
	conn = sqlite3.connect(DB_FILE)
	cursor = conn.cursor()

	print("\n1) Total de clientes")
	cursor.execute("SELECT COUNT(*) FROM clients")
	print(cursor.fetchone()[0])

	print("\n2) Total por risco")
	cursor.execute("SELECT risk, COUNT(*) FROM loans GROUP BY risk")
	for row in cursor.fetchall():
		print(row)

	print("\n3) Top 5 maiores créditos")
	cursor.execute(
		"""
		SELECT c.original_id, l.credit_amount, l.risk
		FROM clients c
		JOIN loans l ON l.client_id = c.id
		ORDER BY l.credit_amount DESC
		LIMIT 5
		"""
	)
	for row in cursor.fetchall():
		print(row)

	print("\n4) Quantos registros têm saving_accounts NULL")
	cursor.execute("SELECT COUNT(*) FROM clients WHERE saving_accounts IS NULL")
	print(cursor.fetchone()[0])

	conn.close()


if __name__ == "__main__":
	run_examples()
