import duckdb
import pandas as pd
from scipy.stats import chi2_contingency
file_path = r'C:\Users\steam\OneDrive\Desktop\PythonApplication1\PythonApplication1\dannye-dlia-keisa-po-pa-cebbefc3-5b29-4f88-b6d4-3336c88d743f.xlsx'

users = pd.read_excel(file_path, sheet_name='Пользователи')
payments = pd.read_excel(file_path, sheet_name='Платежи')


duckdb.query('''
    CREATE OR REPLACE TABLE users_clean AS
    SELECT DISTINCT * FROM users
    WHERE "group" IS NOT NULL AND city IS NOT NULL AND age BETWEEN 14 AND 90
''')

duckdb.query('''
    CREATE OR REPLACE TABLE payments_clean AS
    SELECT p.payment_id, p.user_id, u."group" AS "group",
       p.step1_opened, p.step2_entered, p.step3_confirmed, p.step4_success
FROM payments AS p
JOIN users_clean AS u ON p.user_id = u.user_id
WHERE p.step1_opened >= DATE '2024-04-01'
  AND p.step1_opened <  DATE '2024-05-01'
  AND NOT (p.step2_entered   IS NOT NULL AND p.step1_opened   IS NULL)
  AND NOT (p.step3_confirmed IS NOT NULL AND p.step2_entered  IS NULL)
  AND NOT (p.step4_success   IS NOT NULL AND p.step3_confirmed IS NULL)
''')

result = duckdb.query('''
    SELECT
      u."group",
      COUNT(DISTINCT u.user_id) AS total_users,
      COUNT(DISTINCT CASE WHEN p.step1_opened    IS NOT NULL THEN u.user_id END) AS step1,
      COUNT(DISTINCT CASE WHEN p.step2_entered   IS NOT NULL THEN u.user_id END) AS step2,
      COUNT(DISTINCT CASE WHEN p.step3_confirmed IS NOT NULL THEN u.user_id END) AS step3,
      COUNT(DISTINCT CASE WHEN p.step4_success   IS NOT NULL THEN u.user_id END) AS step4
    FROM users_clean u
    LEFT JOIN payments_clean as p ON u.user_id = p.user_id
    GROUP BY u."group"
''').df()

print(result)


group_a_success = 493
group_a_total = 750
group_b_success = 603
group_b_total = 750

table = [
    [group_a_success, group_a_total - group_a_success],
    [group_b_success, group_b_total - group_b_success]
]

chi2, p_value, dof, expected = chi2_contingency(table)

print("chi2 =", round(chi2, 2))
print("p-value =", p_value)