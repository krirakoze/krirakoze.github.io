# Portfolio reconstruction for Christa Irakoze; not an original course export.
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def calculate(d):
    if not np.isfinite(d[['net_qty','waste_rate','unit_price']].to_numpy()).all():raise ValueError('Nonfinite assumption')
    if (d.net_qty<0).any() or (d.unit_price<0).any() or ((d.waste_rate<0)|(d.waste_rate>=1)).any():raise ValueError('Invalid material assumption')
    d=d.copy();d['gross_qty']=d.net_qty/(1-d.waste_rate);d['net_cost']=d.net_qty*d.unit_price;d['gross_cost']=d.gross_qty*d.unit_price;d['waste_cost']=d.gross_cost-d.net_cost
    return d
def main():
    (H/'data').mkdir(exist_ok=True);(H/'results').mkdir(exist_ok=True)
    path=H/'data/material_assumptions.csv'
    if not path.exists():
        pd.DataFrame([
        ['Polyester mesh','m2',.55,.10,2.4],['Woven polyester','m2',.35,.10,3.2],
        ['Reflective tape','m',4,.05,.38],['Edge binding','m',5,.05,.08],
        ['Front zipper','piece',1,0,.35],['Sewing thread','m',70,.05,.003],
        ['Labels','set',1,0,.05],['Logo consumables','set',1,0,.08]],columns=['component','unit','net_qty','waste_rate','unit_price']).to_csv(path,index=False)
    d=pd.read_csv(path);c=calculate(d);c.to_csv(H/'results/component_costs.csv',index=False)
    total=c.gross_cost.sum();waste=c.waste_cost.sum()
    cases=[]
    for rate in [0,.05,.10,.15,.20]:
        t=d.copy();t.loc[t.component=='Polyester mesh','waste_rate']=rate
        cases.append({'scenario':'mesh waste '+str(rate),'material_cost_per_vest':calculate(t).gross_cost.sum()})
    for change in [-.2,0,.2]:
        t=d.copy();t.loc[t.component=='Polyester mesh','unit_price']*=1+change
        cases.append({'scenario':'mesh price change '+str(change),'material_cost_per_vest':calculate(t).gross_cost.sum()})
    pd.DataFrame(cases).to_csv(H/'results/sensitivity.csv',index=False)
    (H/'results/summary.md').write_text(f'# Synthetic material cost\n\nPer vest: ${total:.6f}\n\nWaste cost: ${waste:.6f}\n\nBatch of 1,000: ${total*1000:.2f}\n\nMaterial only; all inputs synthetic.\n')
    bad=d.copy();bad.loc[0,'waste_rate']=1
    try:calculate(bad)
    except ValueError:pass
    else:raise AssertionError('Waste=1 must fail')
    fig,ax=plt.subplots(figsize=(9,4.7));ax.barh(c.component,c.net_cost,color='#126d78',label='Net material');ax.barh(c.component,c.waste_cost,left=c.net_cost,color='#cf9c53',label='Waste');ax.invert_yaxis();ax.set(xlabel='USD per finished vest',title='Synthetic vest material cost, including waste');ax.legend();fig.tight_layout();fig.savefig(H/'results/material_costs.png',dpi=160);plt.close(fig)
    print(f'Materials: ${total:.6f} per vest; ${waste:.6f} waste')
if __name__=='__main__':main()
