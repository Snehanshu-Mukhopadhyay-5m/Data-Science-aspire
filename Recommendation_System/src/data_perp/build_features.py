import os
import pickle
import pandas as pd
import torch
from sklearn.preprocessing import LabelEncoder as lb

os.makedirs('Recommendation_System/data/processed',exist_ok=True)
os.makedirs('Recommendation_System/data/artifact',exist_ok=True)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


data = {
    'user_id': ['u1', 'u2', 'u1', 'u3', 'u4'],
    'job_id': ['j101', 'j102', 'j103', 'j101', 'j104'],
    'user_skill': ['Python', 'Java', 'Python', 'C++', 'Python'],
    'job_req': ['Python', 'Java', 'C++', 'Python', 'Go'],
    'applied': [1, 1, 0, 1, 0]
}

df = pd.DataFrame(data)

user_encoder = lb()
job_encoder = lb()
skill_encoder = lb()

df['user_idx'] = user_encoder.fit_transform(df['user_id'])
df['job_idx'] = user_encoder.fit_transform(df['job_id'])

all_skills = pd.concat([df['user_skill'],df['job_req']])
skill_encoder.fit(all_skills)

df['user_skill_idx'] = skill_encoder.transform(df['user_skill'])
df['job_req_idx'] = skill_encoder.transform(df['job_req'])

df.to_parquet('data/processed/offline_feature_store.parquet',engine='pyarrow')

with open('artifacts/user_encoder.pkl','wb') as f:
    pickle.dump(user_encoder, f)
with open('artifacts/job_encoder.pkl','wb') as f:
    pickle.dump(job_encoder, f)
with open('artifacts/skill_encoder.pkl','wb') as f:
    pickle.dump(skill_encoder, f)