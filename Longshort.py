#!/usr/bin/env python
# coding: utf-8

# # 读入数据

# In[1]:


import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
get_ipython().run_line_magic('matplotlib', 'inline')
price_c=pd.read_csv('price.csv',encoding='gbk')
barra_c=pd.read_csv('barra.csv',encoding='gbk')
citics_c=pd.read_csv('citics.csv',encoding='gbk')


# In[2]:


pd.set_option('precision',9)


# In[3]:


price_1=price_c[['日期','股票代码','复权收盘价']]
price_0=price_1.set_index(['日期','股票代码'])
date=price_0.index.levels[0]#date是日期序列
datelen=len(date)


# In[4]:


citics_1=citics_c
citics_1['股票代码']=[int(code[0:6]) for code in citics_1['股票代码']]
citics_1=citics_1.set_index('股票代码')
sc=citics_1.index#sc是股票代码序列
sclen=len(sc)


# # 处理数据，日期-股票代码为索引

# # 包含Size，收益率，中信一级行业三列

# # 主要是计算每月个股收益率

# In[5]:


price_1=price_1.set_index(['日期'])
price_d=price_1.groupby('股票代码')


# In[6]:


barra_0=barra_c[['日期','股票代码','Size']]
barra_0=barra_0.set_index(['日期','股票代码'])
price_0['收益率']=np.nan
price_0['中信一级行业']=''


# In[7]:


for i in range(0,datelen-1,1):#这里是计算每个月个股的收益率=(下月股价-本月股价)/本月股价
    t1=date[i]
    t2=date[i+1]
    for j in range(0,sclen,1):#遇到表格里没有的月份-股票会报错，所以这里用try
        scn1=sc[j]
        try:
            price_d.get_group(scn1)
        except:
            pass
        else:
            price_2=price_d.get_group(scn1)
            try:
                price_2['复权收盘价'][t1]
                price_2['复权收盘价'][t2]
            except:
                pass
            else:
                p1=price_2['复权收盘价'][t1]
                p2=price_2['复权收盘价'][t2]
                price_0['收益率'][t1][scn1]=(p2-p1)/p1#收益率
                price_0['中信一级行业'][t1][scn1]=citics_1['中信一级行业'][scn1]
                #顺便把行业也标上


# In[8]:


p_b=pd.concat([barra_0,price_0],axis=1)
p_b=p_b[['Size','收益率','中信一级行业']]
p_b=p_b.dropna()
p_b


# # 计算市值因子收益率

# In[9]:


p_b_d=p_b.groupby('日期')
rin1=np.zeros(datelen-1)
rin2=np.zeros(datelen-1)
rin3=np.zeros(datelen-1)
rin4=np.zeros(datelen-1)
rin5=np.zeros(datelen-1)


# In[10]:


def longshort(s_r,i):#提供数据s_r，i,计算第i段的市值因子收益率
    #sp=pd.qcut(s_r['Size'],[0,0.2,0.8,1],labels=[1,0,-1])     qcut处理重复数据会报错
    n=len(s_r)
    m=[0,0,0,0,0,0]
    m[0]=0#0
    m[1]=int(n/5)#1/5
    m[2]=m[1]*2#2/5
    m[3]=n-m[2]#3/5
    m[4]=n-m[1]#4/5
    m[5]=n#1
    l=0
    nl=0
    s_r_sorted=s_r.sort_values('Size')
    for j in range(m[i-1],m[i],1):
        l=l+s_r_sorted['收益率'][s_r_sorted.index[j]]#多头
        nl+=1
    return l/nl


# In[11]:


#日期-市值因子收益率
r1=p_b.groupby('日期')['Size','收益率'].apply(longshort,1)+1#第1组每月收益率
r2=p_b.groupby('日期')['Size','收益率'].apply(longshort,2)+1#第2组每月收益率
r3=p_b.groupby('日期')['Size','收益率'].apply(longshort,3)+1#第3组每月收益率
r4=p_b.groupby('日期')['Size','收益率'].apply(longshort,4)+1#第4组每月收益率
r5=p_b.groupby('日期')['Size','收益率'].apply(longshort,5)+1#第5组每月收益率
rc1=r1.cumprod()#第1组累积收益率
rc2=r2.cumprod()#第2组累积收益率
rc3=r3.cumprod()#第3组累积收益率
rc4=r4.cumprod()#第4组累积收益率
rc5=r5.cumprod()#第5组累积收益率


# In[12]:


for i in range(0,datelen-1,1):
    p_b_1=p_b_d.get_group(date[i])
    #对于每个日期，计算行业-市值因子收益率的平均
    #第1组每月收益率
    rin1[i]=p_b_1.groupby('中信一级行业')['收益率','Size'].apply(longshort,1).mean()+1
    #第2组每月收益率
    rin2[i]=p_b_1.groupby('中信一级行业')['收益率','Size'].apply(longshort,2).mean()+1
    #第3组每月收益率
    rin3[i]=p_b_1.groupby('中信一级行业')['收益率','Size'].apply(longshort,3).mean()+1
    #第4组每月收益率
    rin4[i]=p_b_1.groupby('中信一级行业')['收益率','Size'].apply(longshort,4).mean()+1
    #第5组每月收益率
    rin5[i]=p_b_1.groupby('中信一级行业')['收益率','Size'].apply(longshort,5).mean()+1
rcin1=rin1.cumprod()#第1组累积收益率
rcin2=rin2.cumprod()#第2组累积收益率
rcin3=rin3.cumprod()#第3组累积收益率
rcin4=rin4.cumprod()#第4组累积收益率
rcin5=rin5.cumprod()#第5组累积收益率


# In[13]:


rls=r1-r5+1#多空净值
rinls=rin1-rin5+1#行业中性多空净值
rcls=rls.cumprod()
rcinls=rinls.cumprod()


# # 计算年化超额收益和月胜率

# In[14]:


r=p_b.groupby('日期')['收益率'].agg('mean')+1
rc=r.cumprod()
#市场平均


# In[15]:


f=pd.DataFrame(index=['第1组','第2组','第3组','第4组','第5组'],columns=['年化超额收益%','月胜率%'])
fin=pd.DataFrame(index=['第1组','第2组','第3组','第4组','第5组'],columns=['年化超额收益%','月胜率%'])


# In[16]:


#市值因子
f['年化超额收益%']['第1组']=(rc1[date[datelen-2]]-rc[date[datelen-2]])/8.5*100
f['年化超额收益%']['第2组']=(rc2[date[datelen-2]]-rc[date[datelen-2]])/8.5*100
f['年化超额收益%']['第3组']=(rc3[date[datelen-2]]-rc[date[datelen-2]])/8.5*100
f['年化超额收益%']['第4组']=(rc4[date[datelen-2]]-rc[date[datelen-2]])/8.5*100
f['年化超额收益%']['第5组']=(rc5[date[datelen-2]]-rc[date[datelen-2]])/8.5*100
f['月胜率%']['第1组']=(r1>r).value_counts()[True]/(datelen-1)*100
f['月胜率%']['第2组']=(r2>r).value_counts()[True]/(datelen-1)*100
f['月胜率%']['第3组']=(r3>r).value_counts()[True]/(datelen-1)*100
f['月胜率%']['第4组']=(r4>r).value_counts()[True]/(datelen-1)*100
f['月胜率%']['第5组']=(r5>r).value_counts()[True]/(datelen-1)*100


# In[17]:


#行业中性
fin['年化超额收益%']['第1组']=(rcin1[datelen-2]-rc[date[datelen-2]])/8.5*100
fin['年化超额收益%']['第2组']=(rcin2[datelen-2]-rc[date[datelen-2]])/8.5*100
fin['年化超额收益%']['第3组']=(rcin3[datelen-2]-rc[date[datelen-2]])/8.5*100
fin['年化超额收益%']['第4组']=(rcin4[datelen-2]-rc[date[datelen-2]])/8.5*100
fin['年化超额收益%']['第5组']=(rcin5[datelen-2]-rc[date[datelen-2]])/8.5*100
fin['月胜率%']['第1组']=(rin1>r).value_counts()[True]/(datelen-1)*100
fin['月胜率%']['第2组']=(rin2>r).value_counts()[True]/(datelen-1)*100
fin['月胜率%']['第3组']=(rin3>r).value_counts()[True]/(datelen-1)*100
fin['月胜率%']['第4组']=(rin4>r).value_counts()[True]/(datelen-1)*100
fin['月胜率%']['第5组']=(rin5>r).value_counts()[True]/(datelen-1)*100


# # 市值因子多空组合累积收益率-日期曲线

# In[18]:


date_1=[str(i)[0:4]+'-'+str(i)[4:6]+'-'+str(i)[6:8] for i in date]
xs=[pd.Timestamp(d) for d in date_1]


# 这里是五组市值因子组合的累积收益率曲线，Longshort1为市值最小的组，Longshort5为市值最大的组,Market是市场平均

# In[19]:


plt.figure(figsize=(16,8))
plt.plot(xs[0:-1],rc1*100,linewidth=1,color='blue',label='Longshort1')
plt.plot(xs[0:-1],rc2*100,linewidth=1,color='red',label='Longshort2')
plt.plot(xs[0:-1],rc3*100,linewidth=1,color='yellow',label='Longshort3')
plt.plot(xs[0:-1],rc4*100,linewidth=1,color='orange',label='Longshort4')
plt.plot(xs[0:-1],rc5*100,linewidth=1,color='green',label='Longshort5')
plt.plot(xs[0:-1],rc*100,linewidth=2,color='black',label='Market')
plt.xlabel('Date',fontsize=20)
plt.ylabel('Rate%',fontsize=20)
plt.suptitle('Rate-Date-Longshort', size=20, y=1.03)
plt.hlines(y=[0,100,200,300,400,500,600,700,800,900,1000,1100,1200],xmin=xs[0],xmax=xs[-1],color='grey')
plt.legend()
f
#plot不能显示中文。。。好像跟字体有关


# 这里是五组行业中性市值因子组合的累积收益率曲线，Industry neutral1为市值最小的组，Industry neutral5为市值最大的组,Market是市场平均

# In[20]:


plt.figure(figsize=(16,8))
plt.plot(xs[0:-1],rcin1*100,linewidth=1,color='blue',linestyle='--',label='Industry neutral1')
plt.plot(xs[0:-1],rcin2*100,linewidth=1,color='red',linestyle='--',label='Industry neutral2')
plt.plot(xs[0:-1],rcin3*100,linewidth=1,color='yellow',linestyle='--',label='Industry neutral3')
plt.plot(xs[0:-1],rcin4*100,linewidth=1,color='orange',linestyle='--',label='Industry neutral4')
plt.plot(xs[0:-1],rcin5*100,linewidth=1,color='green',linestyle='--',label='Industry neutral5')
plt.plot(xs[0:-1],rc*100,linewidth=2,color='black',label='Market')
plt.xlabel('Date',fontsize=20)
plt.ylabel('Rate%',fontsize=20)
plt.suptitle('Rate-Date-Industry neutral', size=20, y=1.03)
plt.hlines(y=[0,100,200,300,400,500,600,700,800,900,1000,1100,1200],xmin=xs[0],xmax=xs[-1],color='grey')
plt.legend()
fin


# 这里市值因子的多空组合净值与行业中性条件下的多空组合净值

# In[21]:


plt.figure(figsize=(16,8))
plt.plot(xs[0:-1],rcls*100,linewidth=1,color='blue',label='Longshort')
plt.plot(xs[0:-1],rcinls*100,linewidth=1,color='red',linestyle='--',label='Industry neutral')
plt.plot(xs[0:-1],rc*100,linewidth=2,color='black',label='Market')
plt.xlabel('Date',fontsize=20)
plt.ylabel('Rate%',fontsize=20)
plt.suptitle('Rate-Date', size=20, y=1.03)
plt.hlines(y=[0,100,200,300,400,500,600,700,800,900,1000,1100,1200],xmin=xs[0],xmax=xs[-1],color='grey')
plt.legend()


# 多空组合净值年化超额收益

# In[22]:


f['年化超额收益%']['第1组']-f['年化超额收益%']['第5组']


# 行业中性条件下的多空组合净值年化超额收益

# In[23]:


fin['年化超额收益%']['第1组']-fin['年化超额收益%']['第5组']


# 多空组合净值收益高于行业中性条件下收益
# 行业中性条件下第1组的收益更低，第5组的亏损也更低
