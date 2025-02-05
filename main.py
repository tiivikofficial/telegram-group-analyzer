import asyncio
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from telethon.sync import TelegramClient
from telethon.tl.types import ChannelParticipantsRecent, MessageEntityUrl
from config import API_ID, API_HASH, GROUP_USERNAME, SESSION_NAME

async def fetch_group_data():
    async with TelegramClient(SESSION_NAME, API_ID, API_HASH) as client:
        group = await client.get_entity(GROUP_USERNAME)
        
        participants = await client.get_participants(group, aggressive=True)
        messages = [msg async for msg in client.iter_messages(group, limit=2000)]
        
        user_activity = {}
        for msg in messages:
            if not msg.sender_id:
                continue
                
            if msg.sender_id not in user_activity:
                user_activity[msg.sender_id] = {
                    'username': next((p.username for p in participants if p.id == msg.sender_id), 'Unknown'),
                    'messages': 0,
                    'chars': 0,
                    'media': 0,
                    'links': 0,
                    'reactions': 0,
                    'timestamps': []
                }
            
            user = user_activity[msg.sender_id]
            user['messages'] += 1
            user['chars'] += len(msg.text or '')
            user['timestamps'].append(msg.date)
            
            if msg.media:
                user['media'] += 1
            if msg.entities:
                user['links'] += sum(1 for e in msg.entities if isinstance(e, MessageEntityUrl))
            if msg.reactions:
                user['reactions'] += sum(
                    reaction.count 
                    for reaction in msg.reactions.results 
                    if hasattr(reaction, 'count')
                )

        return user_activity

def analyze_activity(user_activity):
    df = pd.DataFrame.from_dict(user_activity, orient='index')
    
    # Calculate engagement metrics
    df['avg_length'] = df['chars'] / df['messages']
    df['activity_rate'] = df['messages'] / df['timestamps'].apply(
        lambda x: (max(x) - min(x)).total_seconds()/3600 if len(x)>1 else 1
    )
    # Spam detection algorithm
    df['spam_score'] = (
        df['messages'] * 0.4 + 
        (1 - df['avg_length']/100) * 0.3 + 
        (1 - df['media']/df['messages'].clip(lower=1)) * 0.2 + 
        df['links'] * 0.1
    )
    
    return df.sort_values('spam_score', ascending=False)

def visualize_results(df):
    plt.figure(figsize=(20, 15))
    plt.suptitle('Telegram Group Activity Analysis', fontsize=18)
    
    # Top active users
    plt.subplot(2,2,1)
    top_users = df.nlargest(10, 'messages')
    sns.barplot(x=top_users.index, y=top_users['messages'], hue=top_users['username'], dodge=False)
    plt.xticks(rotation=45)
    plt.title('Top 10 active users by message count')
    
    # Spam distribution
    plt.subplot(2,2,2)
    sns.scatterplot(x='messages', y='spam_score', size='avg_length', hue='media', data=df)
    plt.title('Spam Score Distribution')
    
    # Activity time pattern
    plt.subplot(2,2,3)
    all_times = [t.hour for sublist in df['timestamps'] for t in sublist]
    sns.histplot(all_times, bins=24, kde=True)
    plt.title('Hourly Activity Pattern')
    plt.xlabel('Hour of Day')
    
    # Content type distribution
    plt.subplot(2,2,4)
    content_mix = df[['media', 'links']].sum().to_frame().T
    content_mix.plot(kind='bar', stacked=True)
    plt.title('Content Type Distribution')
    plt.xticks([])
    
    plt.tight_layout()
    plt.show()

async def main():
    user_activity = await fetch_group_data()
    analyzed_df = analyze_activity(user_activity)
    visualize_results(analyzed_df)
    
    print(analyzed_df[['username', 'messages', 'spam_score', 'media', 'links']].head(10))

if __name__ == '__main__':
    asyncio.run(main())