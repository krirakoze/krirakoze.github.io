# Portfolio reconstruction for Christa Irakoze; not an original course export.
from pathlib import Path
import json
import numpy as np,pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def decide(current,predicted,tank_fraction,threshold=.03):
    if not 0<=tank_fraction<=1:raise ValueError('Tank fraction must be between 0 and 1')
    if tank_fraction<=.15:return 'Prioritize refueling: low-tank override'
    change=predicted-current
    if change>threshold:return 'Buy now: predicted increase exceeds demo threshold'
    if change < -threshold:return 'Consider waiting: predicted decrease exceeds demo threshold'
    return 'No strong price signal: difference within demo uncertainty zone'
def main():
    (H/'data').mkdir(exist_ok=True);(H/'results').mkdir(exist_ok=True)
    r=np.random.default_rng(42);n=180;t=np.arange(n)
    prices=3.25+.16*np.sin(t/8)+.001*t+np.cumsum(r.normal(0,.025,n))
    d=pd.DataFrame({'week':pd.date_range('2022-01-03',periods=n,freq='W-MON'),'price':prices})
    d.to_csv(H/'data/synthetic_weekly_prices.csv',index=False)
    for k in [1,2,4]:d['lag'+str(k)]=d.price.shift(k)
    d['rolling4']=d.price.shift(1).rolling(4).mean()
    d=d.dropna();cols=['lag1','lag2','lag4','rolling4'];split=int(len(d)*.8)
    tr,te=d.iloc[:split],d.iloc[split:]
    ridge=Ridge(alpha=1).fit(tr[cols],tr.price)
    forest=RandomForestRegressor(n_estimators=100,max_depth=4,random_state=42,n_jobs=1).fit(tr[cols],tr.price)
    preds={'Persistence':te.lag1.to_numpy(),'Ridge':ridge.predict(te[cols]),'Random forest':forest.predict(te[cols])}
    preds['Equal-weight ensemble']=(preds['Ridge']+preds['Random forest'])/2
    metrics=[{'model':k,'mae_usd_per_gallon':mean_absolute_error(te.price,v),'data_type':'synthetic'} for k,v in preds.items()]
    pd.DataFrame(metrics).to_csv(H/'results/model_metrics.csv',index=False)
    out=te[['week','price','lag1']].copy()
    for k,v in preds.items():out[k]=v
    out.to_csv(H/'results/holdout_forecasts.csv',index=False)
    latest=float(d.price.iloc[-1]);feat=pd.DataFrame([[latest,float(d.price.iloc[-2]),float(d.price.iloc[-4]),float(d.price.iloc[-4:].mean())]],columns=cols)
    nxt=float((ridge.predict(feat)[0]+forest.predict(feat)[0])/2)
    report={'data_type':'synthetic','forecast_horizon':'one week','current_price':latest,'predicted_next_price':nxt,'tank_fraction_demo':.5,'threshold_demo':.03,'decision':decide(latest,nxt,.5),'low_tank_example':decide(latest,nxt,.1),'live_EIA_connection':False,'achieved_savings':None}
    (H/'results/decision.json').write_text(json.dumps(report,indent=2))
    assert decide(3,3.01,.5).startswith('No strong') and decide(3,2.9,.1).startswith('Prioritize')
    fig,ax=plt.subplots(figsize=(10,4.7));ax.plot(te.week,te.price,label='Actual synthetic price',color='#233344',lw=2);ax.plot(te.week,preds['Equal-weight ensemble'],label='Ensemble forecast',color='#126d78');ax.plot(te.week,preds['Persistence'],label='Persistence',ls='--',color='#b0803f');ax.set(ylabel='USD per gallon',title='Chronological holdout on fictional weekly prices');ax.legend();fig.autofmt_xdate();fig.tight_layout();fig.savefig(H/'results/forecast.png',dpi=160);plt.close(fig)
    print('Gas: chronological benchmark and decision-rule checks passed; all data synthetic')
if __name__=='__main__':main()
