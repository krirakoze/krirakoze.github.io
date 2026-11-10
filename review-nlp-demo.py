# Portfolio reconstruction for Christa Irakoze; not an original course export.
from pathlib import Path
import re,argparse,json
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
H=Path(__file__).resolve().parent
PATTERN=re.compile(r"upsell|up-sell|up sell|push(?:y|ed|ing)?|pressure|sell me|unnecessary|didn'?t need|quoted me",re.I)
def main():
    a=argparse.ArgumentParser();a.add_argument('--input',type=Path);args=a.parse_args()
    (H/'data').mkdir(exist_ok=True);(H/'results').mkdir(exist_ok=True)
    d=pd.DataFrame([
    ['They pressured me to buy repairs I did not need.',True],
    ['There was no pressure and the work was excellent.',False],
    ['The technician quoted me a fair price.',False],
    ['They explained the repairs clearly and finished on time.',False],
    ['The pushy salesperson kept insisting on unnecessary extras.',True],
    ['I felt forced to buy an extra service before I could leave.',True]],columns=['text','illustrative_unwanted_pressure'])
    d.to_csv(H/'data/fictional_reviews.csv',index=False)
    d['keyword_flag']=d.text.map(lambda t:bool(PATTERN.search(t)))
    d['error_type']=d.apply(lambda r:'false positive' if r.keyword_flag and not r.illustrative_unwanted_pressure else 'false negative' if not r.keyword_flag and r.illustrative_unwanted_pressure else 'agreement',axis=1)
    d.to_csv(H/'results/keyword_audit.csv',index=False)
    assert d.error_type.eq('false positive').sum()==2 and d.error_type.eq('false negative').sum()==1
    m=pd.DataFrame([['Negative',.90,.93,.91,1322],['Positive',.95,.93,.94,1940]],columns=['class','precision','recall','f1','support'])
    m.to_csv(H/'results/source_reported_metrics.csv',index=False)
    fig,ax=plt.subplots(figsize=(8,4.7));m.set_index('class')[['precision','recall','f1']].plot.bar(ax=ax,color=['#126d78','#cf9c53','#566881']);ax.set(ylim=(0,1),ylabel='Score',title='Historical source-reported rating-polarity metrics\nNot an upsell-detection evaluation');ax.tick_params(axis='x',rotation=0);fig.tight_layout();fig.savefig(H/'results/source_metrics.png',dpi=160);plt.close(fig)
    if args.input:
        from sklearn.model_selection import train_test_split
        from sklearn.feature_extraction.text import CountVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import make_pipeline
        from sklearn.metrics import classification_report
        x=pd.read_csv(args.input).dropna(subset=['text','stars']);x=x[x.stars.isin([1,2,4,5])];y=(x.stars>=4).astype(int)
        if y.nunique()!=2 or y.value_counts().min()<10:raise ValueError('Need >=10 reviews of each polarity')
        xt,xv,yt,yv=train_test_split(x.text.astype(str),y,test_size=.2,random_state=5,stratify=y)
        model=make_pipeline(CountVectorizer(stop_words='english',max_features=800,token_pattern=r'(?u)\b[a-zA-Z]+\b'),MultinomialNB())
        model.fit(xt,yt);report=classification_report(yv,model.predict(xv),output_dict=True,zero_division=0)
        (H/'results/user_data_metrics.json').write_text(json.dumps(report,indent=2))
    print('NLP synthetic audit: 2 false positives and 1 false negative; historical metrics chart exported')
if __name__=='__main__':main()
