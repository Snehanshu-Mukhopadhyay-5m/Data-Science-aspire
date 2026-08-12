import torch 
import torch.nn as nn
import torch.nn.functional as NF

class TwoTower(nn.Module):
    def __init__(self,num_users,num_jobs,num_skills,embedding_dim=32):
        super(TwoTower,self).__init__()

        self.user_embedding = nn.Embedding(num_embedding=num_users,embedding_dim=embedding_dim)
        self.user_skill_embedding = nn.Embedding(num_embedding=num_skills,embedding_dim=embedding_dim)


        self.job_embedding = nn.Embedding(num_embedding=num_jobs,embedding_dim=embedding_dim)
        self.job_req_embedding = nn.Embedding(num_embedding=num_skills,embedding_dim=embedding_dim)


        self.job_embedding = nn.Embedding(num_embedding=num_jobs,embedding_dim=embedding_dim)
        self.job_req_embedding = nn.Embedding(num_embedding=num_skills,embedding_dim=embedding_dim)             

        