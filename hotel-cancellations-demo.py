# Portfolio reconstruction for Christa Irakoze; not an original course export.
from pathlib import Path
import argparse,json
import numpy as np,pandas as pd
from sklearn.model_selection import train_test_split,GridSearchCV,StratifiedKFold
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_auc_score,ConfusionMatrixDisplay
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
def fictional():
    r=np.random.default_rng(42);n=1200
    d=pd.DataFrame({'lead_time':r.integers(0,300,n),'adr':r.uniform(60,260,n).round(2),'adults':r.integers(1,5,n),'previous_cancellations':r.binomial(2,.12,n),'hotel':r.choice(['Resort Hotel','City Hotel'],n),'market_segment':r.choice(['Direct','Online TA','Corporate'],n),'deposit_type':r.choice(['No Deposit','Non Refund'],n,p=[.8,.2])})
    z=-2+.009*d.lead_time+.55*d.previous_cancellations+.55*(d.market_segment=='Online TA')-1.2*(d.deposit_type=='Non Refund')
    d['is_canceled']=r.binomial(1,1/(1+np.exp(-z)));return d
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',type=Path);a=ap.parse_args()
    (H/'data').mkdir(exist_ok=True);(H/'results').mkdir(exist_ok=True)
    d=pd.read_csv(a.input) if a.input else fictional()
    if not a.input:d.to_csv(H/'data/synthetic_bookings.csv',index=False)
    num=['lead_time','adr','adults','previous_cancellations'];cat=['hotel','market_segment','deposit_type']
    if not d.is_canceled.isin([0,1]).all():raise ValueError('Target must be binary')
    x=d[num+cat];y=d.is_canceled
    xt,xv,yt,yv=train_test_split(x,y,test_size=.2,random_state=42,stratify=y)
    def prep():return ColumnTransformer([('num',Pipeline([('impute',SimpleImputer(strategy='median')),('scale',StandardScaler())]),num),('cat',Pipeline([('impute',SimpleImputer(strategy='most_frequent')),('encode',OneHotEncoder(handle_unknown='ignore'))]),cat)])
    cv=StratifiedKFold(n_splits=3,shuffle=True,random_state=42)
    tree=GridSearchCV(Pipeline([('preprocess',prep()),('model',DecisionTreeClassifier(random_state=42))]),{'model__max_depth':[3,5,7],'model__min_samples_leaf':[10,25]},cv=cv,scoring='f1',n_jobs=1).fit(xt,yt)
    models={'Pruned tree':tree.best_estimator_,'KNN':Pipeline([('preprocess',prep()),('model',KNeighborsClassifier(n_neighbors=15))]),'Logistic regression':Pipeline([('preprocess',prep()),('model',LogisticRegression(max_iter=1000,random_state=42))])}
    metrics=[];fig,axes=plt.subplots(1,3,figsize=(12,4))
    for ax,(name,m) in zip(axes,models.items()):
        if name!='Pruned tree':m.fit(xt,yt)
        pred=m.predict(xv);proba=m.predict_proba(xv)[:,1]
        metrics.append(dict(model=name,accuracy=accuracy_score(yv,pred),precision=precision_score(yv,pred,zero_division=0),recall=recall_score(yv,pred,zero_division=0),f1=f1_score(yv,pred,zero_division=0),roc_auc=roc_auc_score(yv,proba)))
        ConfusionMatrixDisplay.from_predictions(yv,pred,ax=ax,colorbar=False,cmap='Blues');ax.set_title(name)
    pd.DataFrame(metrics).to_csv(H/'results/model_metrics.csv',index=False)
    fig.suptitle('Synthetic booking data: held-out results' if not a.input else 'User-provided data: held-out results');fig.tight_layout();fig.savefig(H/'results/confusion_matrices.png',dpi=160);plt.close(fig)
    (H/'results/metadata.json').write_text(json.dumps({'data_type':'synthetic' if not a.input else 'user-provided','rows':len(d),'train_rows':len(xt),'test_rows':len(xv),'seed':42,'tree_selected_parameters':tree.best_params_,'selection_metric':'training CV F1','test_used_for_selection':False,'original_course_metrics':None},indent=2))
    print('Hotel: three pipelines evaluated; synthetic' if not a.input else 'Hotel: user data evaluated')
if __name__=='__main__':main()
