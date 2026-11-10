# Portfolio reconstruction for Christa Irakoze; not an original course export.
from pathlib import Path
from decimal import Decimal
from datetime import datetime
import csv,json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE=Path(__file__).resolve().parent
def D(x):
    n=Decimal(str(x))
    if not n.is_finite(): raise ValueError('Amount must be finite')
    return n
def project(snapshot,rows):
    at=datetime.fromisoformat(snapshot['snapshot_at'])
    balance=D(snapshot['balance']); minimum=D(snapshot['minimum_balance'])
    if minimum<0: raise ValueError('Minimum must be nonnegative')
    future=[];seen=set()
    for r in rows:
        if r['id'] in seen: raise ValueError('Duplicate transaction ID')
        seen.add(r['id'])
        if r['type'] not in ('income','expense') or r['status'] not in ('cleared','scheduled') or D(r['amount'])<=0:
            raise ValueError('Invalid transaction')
        stamp=datetime.fromisoformat(r['transaction_at'])
        if stamp.tzinfo is None: raise ValueError('Timezone required')
        if r['account']==snapshot['account'] and r['status']=='scheduled':
            if stamp<=at: raise ValueError('Overdue scheduled transaction requires reconciliation')
            future.append((stamp,r))
    future.sort(key=lambda x:x[0])
    if len({t for t,r in future})!=len(future): raise ValueError('Ambiguous equal transaction times')
    lowest=balance;out=[]
    for stamp,r in future:
        change=D(r['amount'])*(1 if r['type']=='income' else -1)
        balance+=change;lowest=min(lowest,balance)
        out.append({**r,'change':str(change),'balance':str(balance)})
    return {'ending':str(balance),'lowest':str(lowest),'shortfall':str(max(D(0),minimum-lowest)),'rows':out}

def main():
    data=HERE/'data';data.mkdir(exist_ok=True)
    snapshot={'account':'checking','snapshot_at':'2026-11-02T18:00:00-07:00','balance':'1650.00','minimum_balance':'100.00'}
    rows=[{'id':'t0','account':'checking','transaction_at':'2026-11-01T08:00:00-07:00','description':'Recorded monthly income','type':'income','amount':'2800.00','status':'cleared'}]
    for i,(time,label,kind,amount) in enumerate([
        ('2026-11-28T09:00:00-07:00','Electricity','expense','150.00'),
        ('2026-11-29T09:00:00-07:00','Insurance','expense','250.00'),
        ('2026-11-30T08:00:00-07:00','Paycheck','income','500.00'),
        ('2026-11-30T17:00:00-07:00','Rent','expense','1100.00')],1):
        rows.append(dict(id='t'+str(i),account='checking',transaction_at=time,description=label,type=kind,amount=amount,status='scheduled'))
    (data/'snapshot.json').write_text(json.dumps(snapshot,indent=2))
    (data/'transactions.json').write_text(json.dumps(rows,indent=2))
    result=project(snapshot,rows)
    assert D(result['ending'])==650 and D(result['lowest'])==650
    reverse=[dict(r) for r in rows];reverse[-1]['transaction_at']='2026-11-30T07:00:00-07:00'
    rev=project(snapshot,reverse);assert D(rev['ending'])==650 and D(rev['lowest'])==150
    stress=[dict(r) for r in rows];stress[-1]['amount']='1800.00'
    short=project(snapshot,stress);assert D(short['ending'])==-50 and D(short['shortfall'])==150
    duplicate=rows+[rows[-1]]
    try: project(snapshot,duplicate)
    except ValueError: pass
    else: raise AssertionError('Duplicate not rejected')
    out=HERE/'results';out.mkdir(exist_ok=True)
    with (out/'projection.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(result['rows'][0]));w.writeheader();w.writerows(result['rows'])
    (out/'verification.json').write_text(json.dumps({'normal':result,'rent_before_paycheck':rev,'shortfall_case':short,'duplicate_rejected':True},indent=2))
    (out/'report.md').write_text('# Fictional November cash-flow report\n\nOpening checking balance: $1,650 as of November 2, 2026, 6 PM Arizona time.\n\nRecorded cleared income: $2,800. Recorded paid expenses: $0; this does not prove no expenses occurred.\n\nProjected ending balance: $650. Lowest balance: $650. Shortfall to $100 minimum: $0.\n\nIncome arrives before rent on November 30. Reversing that order leaves the same ending balance but lowers the intermediate minimum to $150.\n\nThis report is generated offline and has not been emailed or human-approved.\n')
    vals=[1650]+[float(r['balance']) for r in result['rows']]
    fig,ax=plt.subplots(figsize=(9,4.7));ax.plot(range(len(vals)),vals,marker='o',color='#126d78',lw=2.5)
    ax.axhline(100,color='#b34c3e',ls='--',label='$100 minimum')
    ax.set_xticks(range(5),['Snapshot','Nov 28\nElectricity','Nov 29\nInsurance','Nov 30 8 AM\nPaycheck','Nov 30 5 PM\nRent'])
    ax.set(ylabel='Checking balance (USD)',title='Fictional cash-flow projection: timing matters');ax.legend();fig.tight_layout();fig.savefig(out/'cash_flow.png',dpi=160);plt.close(fig)
    print('Finance: ending $650; reversed order minimum $150; stress shortfall $150; validation passed')
if __name__=='__main__': main()
