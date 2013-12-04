'''
Created on Nov 24, 2013

@author: alex
'''
import yaml
import facebook
import pickle

def get_user_token(file = 'user_access_token.yaml'):
    with open(file, 'r') as file:
        doc = yaml.load(file)
    user_token = doc['token']

    return user_token

def get_user_data():
    user_token = get_user_token()
    graph = facebook.GraphAPI(user_token)
    data = []
    
    offset = 0
    statuses = graph.get_object('me/statuses', limit=100, offset=offset)['data']
    
    while len(statuses) > 0:
        for status in statuses:
            if 'message' in status:
                message = status['message']
                likes = 0
                if 'likes' in status:
                    likes = len(status['likes']['data'])
                data.append((likes,message))
        offset += 100
        statuses = graph.get_object('me/statuses', limit=100, offset=offset)['data']
    return data

def main():
    f = open('Data/heidi_status.p', 'wb')
    print get_user_data()
    pickle.dump(get_user_data(), f)
    
if __name__ == '__main__':
    main()
        
