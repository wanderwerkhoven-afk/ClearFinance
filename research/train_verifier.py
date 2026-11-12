"""Train leakage-safe lexical claim verification baseline. Needs real labels."""
from __future__ import annotations
import sys
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, f1_score
from sklearn.model_selection import GroupShuffleSplit
from sklearn.pipeline import Pipeline

REQUIRED={"document_id","premise","hypothesis","label"}
LABELS=("entailment","contradiction","neutral")

def run(path: str) -> None:
    df=pd.read_csv(path).dropna(subset=list(REQUIRED))
    if not REQUIRED.issubset(df.columns):
        raise ValueError(f"Required columns: {sorted(REQUIRED)}")
    if len(set(df.document_id))<6:
        raise ValueError("At least six documents required for train/validation/test splitting")
    if not set(df.label).issubset(LABELS):
        raise ValueError("Unexpected labels; expected entailment/contradiction/neutral")
    df=df.copy()
    df["text"]=(df["premise"].astype(str)+" [SEP] "+df["hypothesis"].astype(str))
    splitter=GroupShuffleSplit(n_splits=1,test_size=.2,random_state=42)
    train_val_idx,test_idx=next(splitter.split(df,df.label,groups=df.document_id))
    train_val=df.iloc[train_val_idx]
    test=df.iloc[test_idx]
    splitter2=GroupShuffleSplit(n_splits=1,test_size=.25,random_state=42)
    train_idx,val_idx=next(splitter2.split(train_val,train_val.label,groups=train_val.document_id))
    train,val=train_val.iloc[train_idx],train_val.iloc[val_idx]
    if len(set(train.label))<2:
        raise ValueError("Training split has fewer than two classes; collect more labeled documents")
    print("Distinct documents:",len(set(train.document_id)),len(set(val.document_id)),len(set(test.document_id)))
    candidates=[.1,1.0,10.0]
    best_c,best_f1=None,-1
    for c in candidates:
        pipeline=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=1,max_features=50000)),
                           ("model",LogisticRegression(C=c,max_iter=1000,class_weight="balanced",random_state=42))])
        pipeline.fit(train.text,train.label)
        f1=f1_score(val.label,pipeline.predict(val.text),labels=LABELS,average="macro",zero_division=0)
        print(f"Validation C={c}: macro F1={f1:.4f}")
        if f1>best_f1:
            best_c,best_f1=c,f1
    model=Pipeline([("tfidf",TfidfVectorizer(ngram_range=(1,2),min_df=1,max_features=50000)),
                    ("model",LogisticRegression(C=best_c,max_iter=1000,class_weight="balanced",random_state=42))])
    model.fit(pd.concat([train,val]).text,pd.concat([train,val]).label)
    preds=model.predict(test.text)
    print("FINAL TEST -- unseen documents only; C selected on validation:",best_c)
    print(classification_report(test.label,preds,labels=LABELS,zero_division=0))
    print("Confusion matrix order:",LABELS)
    print(confusion_matrix(test.label,preds,labels=LABELS))

if __name__=="__main__":
    if len(sys.argv)!=2:
        raise SystemExit("Usage: python research/train_verifier.py claims.csv")
    run(sys.argv[1])
