import os
import sys
import random
from datetime import datetime, timedelta
from decimal import Decimal

# Ensure project root is in path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.config import Config
from backend.db import get_connection
from backend.auth import hash_password
from backend.fraud_engine import score_and_persist_assessment

# Set fixed random seed for reproducibility
random.seed(42)

def run_seed(target_db=None):
    db_name = target_db or Config.DB_NAME
    print(f"[*] Seeding deterministic demo dataset into database: {db_name}...")

    conn = get_connection(db_name)
    cursor = conn.cursor(dictionary=True)

    try:
        # Disable foreign key checks to allow clean reset
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0;")
        tables = [
            "investigation_notes", "investigation_cases", "risk_factors",
            "risk_assessments", "transactions", "merchants", "customers",
            "users", "audit_logs"
        ]
        for t in tables:
            cursor.execute(f"TRUNCATE TABLE {t};")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1;")
        conn.commit()
        print("  [+] Cleared existing tables.")

        # 1. Seed Users
        users_data = [
            ("System Administrator", "admin@fraudshield.local", "Admin@123", "admin"),
            ("Sarah Vance (Lead Analyst)", "investigator@fraudshield.local", "Investigator@123", "investigator"),
            ("Marcus Chen (Risk Analyst)", "marcus@fraudshield.local", "Investigator@123", "investigator")
        ]
        user_ids = {}
        for full_name, email, password, role in users_data:
            pwd_hash = hash_password(password)
            cursor.execute("""
                INSERT INTO users (full_name, email, password_hash, role, is_active, created_at)
                VALUES (%s, %s, %s, %s, TRUE, NOW())
            """, (full_name, email, pwd_hash, role))
            user_ids[email] = cursor.lastrowid
        conn.commit()
        print(f"  [+] Seeded {len(users_data)} users.")

        # 2. Seed Merchants
        merchants_data = [
            ("MERCH-001", "ElectroDepot Online", "Electronics", "New York, USA"),
            ("MERCH-002", "CloudApex SaaS Systems", "Digital Services", "San Francisco, USA"),
            ("MERCH-003", "LuxuryJewels Int.", "Luxury Goods", "Geneva, Switzerland"),
            ("MERCH-004", "AeroGlobal Airlines", "Travel & Airlines", "Atlanta, USA"),
            ("MERCH-005", "BitVault Exchange", "Cryptocurrency", "Singapore, Singapore"),
            ("MERCH-006", "MetroGrocery Mart", "Grocery", "Chicago, USA"),
            ("MERCH-007", "GrandBistro Dining", "Food & Dining", "Paris, France"),
            ("MERCH-008", "CyberPulse Gaming", "Gaming & Entertainment", "Seoul, South Korea"),
            ("MERCH-009", "ModaVogue Apparel", "Apparel", "Milan, Italy"),
            ("MERCH-010", "FastFuel Petroleum", "Fuel & Automotive", "Houston, USA"),
            ("MERCH-011", "UrbanStay Hotels", "Hospitality", "London, UK"),
            ("MERCH-012", "NexusDirect Wholesale", "Wholesale & Business", "Tokyo, Japan")
        ]
        merchant_ids = []
        for ref, name, cat, loc in merchants_data:
            cursor.execute("""
                INSERT INTO merchants (merchant_reference, merchant_name, category, location, created_at)
                VALUES (%s, %s, %s, %s, NOW() - INTERVAL 30 DAY)
            """, (ref, name, cat, loc))
            merchant_ids.append(cursor.lastrowid)
        conn.commit()
        print(f"  [+] Seeded {len(merchants_data)} merchants.")

        # 3. Seed Customers
        customers_data = [
            ("CUST-1001", "Alexander Wright", "alex.wright@example.com", "+1-555-0101"),
            ("CUST-1002", "Elena Rostova", "elena.rostova@example.com", "+1-555-0102"),
            ("CUST-1003", "Devon Miller", "devon.miller@example.com", "+1-555-0103"),
            ("CUST-1004", "Chloe Zhang", "chloe.zhang@example.com", "+1-555-0104"),
            ("CUST-1005", "Jamal Washington", "jamal.w@example.com", "+1-555-0105"),
            ("CUST-1006", "Sophia Martinez", "sophia.m@example.com", "+1-555-0106"),
            ("CUST-1007", "Liam O'Connor", "liam.oc@example.com", "+1-555-0107"),
            ("CUST-1008", "Amina Al-Mansoor", "amina.mansoor@example.com", "+1-555-0108"),
            ("CUST-1009", "Noah Tanaka", "noah.tanaka@example.com", "+1-555-0109"),
            ("CUST-1010", "Isabella Rossi", "isabella.rossi@example.com", "+1-555-0110"),
            ("CUST-1011", "Lucas Silva", "lucas.silva@example.com", "+1-555-0111"),
            ("CUST-1012", "Emma Watson", "emma.watson@example.com", "+1-555-0112"),
            ("CUST-1013", "Vikram Patel", "vikram.patel@example.com", "+1-555-0113"),
            ("CUST-1014", "Zoe Kravitz", "zoe.k@example.com", "+1-555-0114"),
            ("CUST-1015", "Ethan Hunt", "ethan.hunt@example.com", "+1-555-0115"),
            ("CUST-1016", "Maya Angelou", "maya.a@example.com", "+1-555-0116"),
            ("CUST-1017", "Oliver Twist", "oliver.t@example.com", "+1-555-0117"),
            ("CUST-1018", "Grace Hopper", "grace.h@example.com", "+1-555-0118"),
            ("CUST-1019", "Alan Turing", "alan.t@example.com", "+1-555-0119"),
            ("CUST-1020", "Ada Lovelace", "ada.l@example.com", "+1-555-0120")
        ]
        customer_ids = []
        for ref, name, email, phone in customers_data:
            cursor.execute("""
                INSERT INTO customers (customer_reference, full_name, email, phone, created_at)
                VALUES (%s, %s, %s, %s, NOW() - INTERVAL 45 DAY)
            """, (ref, name, email, phone))
            customer_ids.append(cursor.lastrowid)
        conn.commit()
        print(f"  [+] Seeded {len(customers_data)} customers.")

        # 4. Generate Synthetic Transactions
        # Base time: 5 days ago to now
        now = datetime.now()
        base_time = now - timedelta(days=5)

        txns_to_create = []

        # (a) Baseline transactions for all customers (normal activity: 3-8 per customer)
        txn_counter = 1
        for cid in customer_ids:
            num_txns = random.randint(4, 7)
            for i in range(num_txns):
                offset_hours = random.randint(1, 100)
                txn_time = base_time + timedelta(hours=offset_hours)
                mid = random.choice(merchant_ids[:6])  # Familiar merchants
                amount = round(random.uniform(25.0, 350.0), 2)
                txns_to_create.append({
                    "ref": f"TXN-2026-{txn_counter:05d}",
                    "cid": cid,
                    "mid": mid,
                    "amount": amount,
                    "type": "purchase",
                    "status": "approved",
                    "timestamp": txn_time,
                    "channel": random.choice(["online", "pos", "mobile"]),
                    "location": "New York, USA",
                    "country": "US"
                })
                txn_counter += 1

        # (b) Inject High Amount Transactions (> $5000)
        high_amount_cids = [customer_ids[0], customer_ids[2], customer_ids[4]]
        for cid in high_amount_cids:
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": cid,
                "mid": merchant_ids[2],  # Luxury Jewels
                "amount": round(random.uniform(6500.0, 9200.0), 2),
                "type": "purchase",
                "status": "approved",
                "timestamp": now - timedelta(hours=random.randint(6, 24)),
                "channel": "online",
                "location": "Geneva, Switzerland",
                "country": "CH"
            })
            txn_counter += 1

        # (c) Inject Velocity Burst (4 rapid transactions within 5 minutes)
        burst_cid = customer_ids[1]  # Elena Rostova
        burst_base = now - timedelta(hours=14)
        for i in range(4):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": burst_cid,
                "mid": merchant_ids[0],  # ElectroDepot
                "amount": round(random.uniform(400.0, 850.0), 2),
                "type": "purchase",
                "status": "approved",
                "timestamp": burst_base + timedelta(minutes=i),
                "channel": "online",
                "location": "New York, USA",
                "country": "US"
            })
            txn_counter += 1

        # (d) Inject Failed Attempt Pattern (2 declined attempts followed by a large purchase)
        failed_cid = customer_ids[3]  # Chloe Zhang
        failed_base = now - timedelta(hours=8)
        for i in range(2):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": failed_cid,
                "mid": merchant_ids[4],  # BitVault
                "amount": 2500.00,
                "type": "purchase",
                "status": "declined",
                "timestamp": failed_base + timedelta(minutes=i * 4),
                "channel": "online",
                "location": "Singapore, Singapore",
                "country": "SG"
            })
            txn_counter += 1
        
        # Followed by high value
        txns_to_create.append({
            "ref": f"TXN-2026-{txn_counter:05d}",
            "cid": failed_cid,
            "mid": merchant_ids[4],
            "amount": 5500.00,
            "type": "purchase",
            "status": "approved",
            "timestamp": failed_base + timedelta(minutes=15),
            "channel": "online",
            "location": "Singapore, Singapore",
            "country": "SG"
        })
        txn_counter += 1

        # (e) Inject Critical Combos
        # Critical 1: High amount + Velocity + Spike + Novel Merchant (85-95 points)
        crit_cid1 = customer_ids[5]  # Sophia Martinez
        crit_base1 = now - timedelta(hours=5)
        # Prior normal transaction in US
        txns_to_create.append({
            "ref": f"TXN-2026-{txn_counter:05d}",
            "cid": crit_cid1,
            "mid": merchant_ids[5],  # MetroGrocery
            "amount": 55.00,
            "type": "purchase",
            "status": "approved",
            "timestamp": crit_base1 - timedelta(minutes=35),
            "channel": "mobile",
            "location": "Chicago, USA",
            "country": "US"
        })
        txn_counter += 1
        # 3 rapid high-value transactions from London within 6 minutes
        for i in range(3):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": crit_cid1,
                "mid": merchant_ids[2],  # Luxury Jewels (Never seen before)
                "amount": round(random.uniform(7200.0, 9500.0), 2),
                "type": "purchase",
                "status": "approved" if i == 2 else "declined",
                "timestamp": crit_base1 + timedelta(minutes=i * 2),
                "channel": "online",
                "location": "London, UK",
                "country": "GB"
            })
            txn_counter += 1

        # Critical 2: Jamal Washington - Location jump from US to Singapore + BitVault crypto spike + velocity burst (95 pts - Critical)
        crit_cid2 = customer_ids[4]
        crit_base2 = now - timedelta(hours=2)
        # 2 declined attempts 15 minutes prior in US (failed attempts pattern Rule D)
        for i in range(2):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": crit_cid2,
                "mid": merchant_ids[0],
                "amount": 150.00,
                "type": "purchase",
                "status": "declined",
                "timestamp": crit_base2 - timedelta(minutes=18 - i * 3),
                "channel": "online",
                "location": "New York, USA",
                "country": "US"
            })
            txn_counter += 1
        # 4 rapid online attempts within 8 minutes from Singapore (triggers Velocity on 4th)
        for i in range(4):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": crit_cid2,
                "mid": merchant_ids[4],  # BitVault
                "amount": round(random.uniform(6200.0, 8400.0), 2),
                "type": "purchase",
                "status": "declined" if i == 0 else "approved",
                "timestamp": crit_base2 + timedelta(minutes=5 + i * 2),
                "channel": "online",
                "location": "Singapore, Singapore",
                "country": "SG"
            })
            txn_counter += 1

        # High Risk 3: Alexander Wright - rapid purchases exceeding threshold
        crit_cid3 = customer_ids[0]
        crit_base3 = now - timedelta(hours=18)
        for i in range(3):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": crit_cid3,
                "mid": merchant_ids[11], # NexusDirect (novel)
                "amount": 5400.00 if i == 2 else 1200.00,
                "type": "purchase",
                "status": "approved",
                "timestamp": crit_base3 + timedelta(minutes=i * 2),
                "channel": "online",
                "location": "Tokyo, Japan",
                "country": "JP"
            })
            txn_counter += 1

        # High Risk 4: Devon Miller (CUST-1003) - failed streak then large spike
        crit_cid4 = customer_ids[2]
        crit_base4 = now - timedelta(hours=10)
        for i in range(2):
            txns_to_create.append({
                "ref": f"TXN-2026-{txn_counter:05d}",
                "cid": crit_cid4,
                "mid": merchant_ids[3], # AeroGlobal
                "amount": 2800.00,
                "type": "purchase",
                "status": "declined",
                "timestamp": crit_base4 + timedelta(minutes=i * 5),
                "channel": "online",
                "location": "Atlanta, USA",
                "country": "US"
            })
            txn_counter += 1
        txns_to_create.append({
            "ref": f"TXN-2026-{txn_counter:05d}",
            "cid": crit_cid4,
            "mid": merchant_ids[3],
            "amount": 6200.00,
            "type": "purchase",
            "status": "approved",
            "timestamp": crit_base4 + timedelta(minutes=15),
            "channel": "online",
            "location": "Atlanta, USA",
            "country": "US"
        })
        txn_counter += 1

        # Sort transactions chronologically
        txns_to_create.sort(key=lambda x: x["timestamp"])

        print(f"  [+] Inserting and scoring {len(txns_to_create)} synthetic transactions chronologically...")
        
        created_txn_ids = []
        for t in txns_to_create:
            cursor.execute("""
                INSERT INTO transactions (
                    transaction_reference, customer_id, merchant_id, amount, currency,
                    transaction_type, transaction_status, transaction_timestamp,
                    channel, location, country_code, created_at
                ) VALUES (%s, %s, %s, %s, 'USD', %s, %s, %s, %s, %s, %s, %s)
            """, (
                t["ref"], t["cid"], t["mid"], t["amount"], t["type"],
                t["status"], t["timestamp"], t["channel"], t["location"],
                t["country"], t["timestamp"]
            ))
            txn_id = cursor.lastrowid
            created_txn_ids.append(txn_id)

            # Score each transaction with the real fraud engine!
            score_and_persist_assessment(cursor, txn_id)
        
        conn.commit()
        print(f"  [+] All {len(created_txn_ids)} transactions scored and persisted.")

        # 5. Enrich Investigation Cases with realistic statuses, assignments, and notes
        cursor.execute("SELECT id, transaction_id, priority FROM investigation_cases ORDER BY id")
        cases = cursor.fetchall()
        print(f"  [+] Found {len(cases)} generated investigation cases. Updating case lifecycle...")

        analyst_sarah = user_ids["investigator@fraudshield.local"]
        analyst_marcus = user_ids["marcus@fraudshield.local"]

        for idx, case in enumerate(cases):
            cid = case["id"]
            if idx % 4 == 0:
                # Mark as investigating
                assigned = analyst_sarah if idx % 2 == 0 else analyst_marcus
                cursor.execute("""
                    UPDATE investigation_cases
                    SET case_status = 'investigating', assigned_to = %s, updated_at = NOW()
                    WHERE id = %s
                """, (assigned, cid))
                cursor.execute("""
                    INSERT INTO investigation_notes (case_id, user_id, note_text, created_at)
                    VALUES (%s, %s, 'Contacted cardholder to verify recent international authorization.', NOW() - INTERVAL 2 HOUR)
                """, (cid, assigned))
            elif idx % 4 == 1:
                # Resolved Fraud
                assigned = analyst_sarah
                res_note = "Confirmed unauthorized transaction. Cardholder card cancelled and chargeback dispute initiated."
                cursor.execute("""
                    UPDATE investigation_cases
                    SET case_status = 'resolved_fraud', assigned_to = %s, resolution_notes = %s,
                        resolved_at = NOW() - INTERVAL 1 HOUR, updated_at = NOW() - INTERVAL 1 HOUR
                    WHERE id = %s
                """, (assigned, res_note, cid))
                cursor.execute("""
                    INSERT INTO investigation_notes (case_id, user_id, note_text, created_at)
                    VALUES (%s, %s, %s, NOW() - INTERVAL 1 HOUR)
                """, (cid, assigned, res_note))
            elif idx % 4 == 2:
                # Resolved Legitimate
                assigned = analyst_marcus
                res_note = "Cardholder verified they were traveling and authenticated this high-value luxury purchase via 2FA."
                cursor.execute("""
                    UPDATE investigation_cases
                    SET case_status = 'resolved_legitimate', assigned_to = %s, resolution_notes = %s,
                        resolved_at = NOW() - INTERVAL 3 HOUR, updated_at = NOW() - INTERVAL 3 HOUR
                    WHERE id = %s
                """, (assigned, res_note, cid))
                cursor.execute("""
                    INSERT INTO investigation_notes (case_id, user_id, note_text, created_at)
                    VALUES (%s, %s, %s, NOW() - INTERVAL 3 HOUR)
                """, (cid, assigned, res_note))
            else:
                # Leave Open
                pass

        conn.commit()

        # Print summary KPI
        cursor.execute("SELECT * FROM v_dashboard_summary")
        kpi = cursor.fetchone()
        print("\n========================================================")
        print("  FRAUDSHIELD DEMO SEEDING COMPLETED SUCCESSFULLY")
        print("========================================================")
        print(f"  Total Transactions:     {kpi['total_transactions']}")
        print(f"  Total Volume:           ${float(kpi['total_volume_amount']):,.2f}")
        print(f"  Flagged Transactions:   {kpi['flagged_transactions']}")
        print(f"  Critical Transactions:  {kpi['critical_transactions']}")
        print(f"  Pending Cases:          {kpi['pending_cases']}")
        print(f"  Fraud Rate:             {kpi['fraud_rate_percentage']}%")
        print("========================================================")
        print("  Demo Credentials:")
        print("  - Admin:        admin@fraudshield.local / Admin@123")
        print("  - Investigator: investigator@fraudshield.local / Investigator@123")
        print("========================================================\n")

    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    db_target = sys.argv[1] if len(sys.argv) > 1 else None
    run_seed(db_target)
