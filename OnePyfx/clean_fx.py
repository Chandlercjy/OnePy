df = pd.read_csv('EUR_USD.csv')

df['Date'] = df['Date'].astype('str')
df['Timestamp'] = df['Timestamp'].astype('str')

ind = df['Date']+' ' + df['Timestamp']

ind.name='Date'

df2 = df.set_index(ind)[['Open','High','Low','Close','Volume']]


df2.index= pd.DatetimeIndex(df2.index)

df2.to_csv('EURUSD_cleaned.csv')
