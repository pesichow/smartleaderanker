import pandas as pd

def score_leads(df):
    df.columns = df.columns.str.strip().str.title()

    def score(row):
        score = 0
        try:
            # Deal Stage maps to 'Funding Stage' in our logic
            if row.get('Deal Stage') in ['Series A', 'Series B', 'Series C']:
                score += 2
            if row.get('Funding Amount', 0) >= 1000000:
                score += 3
            if row.get('Employees', 0) >= 50:
                score += 2
            if str(row.get('Industry', '')).lower() == 'saas':
                score += 1
            if str(row.get('City', '')).lower() in ['bangalore', 'san francisco', 'new york']:
                score += 1
        except Exception as e:
            print(f"Row error: {e}")
        return score

    df['Lead Score'] = df.apply(score, axis=1)
    return df.sort_values(by='Lead Score', ascending=False)
