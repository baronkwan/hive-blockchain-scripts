import requests
from datetime import datetime, timedelta
import time
import pandas as pd

nodes = ['https://anyx.io/', 'https://api.hive.blog',
         "https://api.deathwing.me"]
base_url = 'https://hiveblocks.com'

# get posts in user defined post age range
# max limit = 100, otherwise requests returns error

def get_posts_in_age_range(voter=None, target_tag="leofinance", days_old=1, days_before_cashout=5, limit=100):
    """ get_posts_in_age_range => return search result in array[] form
        :param str target_tag: Defines the target tag on hive.blog
        :param int days_old: Defines the post age in days since created
        :param int days_before_cashout: Defines the remaining days before cashout time 
        :param int limit: Defines the number of target tag posts search within a request
    """
      
    # store posts that meet query requirements
    posts_filtered = []
    # check if limit exceed 100
    if limit > 100:
        print("Max limit should not exceed 100.")
        return  # stop search

    # preset query for posts that used leofinance tag with
    # method = get_post_discussions_by_payout / get_discussions_by_trending
    data = {
        "jsonrpc": "2.0",
        # "method":"condenser_api.get_post_discussions_by_payout",
        "method": "condenser_api.get_discussions_by_trending",
        "params": [{"tag": target_tag, "limit": limit}],
        "id": 1
    }
    # POST request to hive blog condenser API
    r = requests.post(nodes[2], json=data)
    queryResult = r.json()['result']

    match_count = 0
    post_search_limit = limit
    # create an empty DataFrame with columns
    posts_filtered_df = pd.DataFrame(columns=[
                                     'id', 'author', 'permlink', 'pending_value_hbd', 'remaining_time_until_cashout', 'voted'])

    if voter == None:
      print('No voter input.')

    print(
        f'\nSearching posts with [leofinance] tag, age {days_old}D old and payout in {days_before_cashout}D.')


    # keywords : post_payout, trending
    for post in queryResult:
        post_author = post['author']
        post_permlink = post['permlink']

        post_voted = False
        # Check if post is voted or not
        if voter != None:
          for i in post['active_votes']:
              if voter in i['voter']:
                  post_voted = True

        # post_json_metadata = post['json_metadata']

        post_created = datetime.fromisoformat(post['created'])
        now = datetime.now()
        post_cashout_time = datetime.fromisoformat(post['cashout_time'])

        post_age = now - post_created
        post_cashout_time_remaining = post_cashout_time - now

        # check if post is older than x days and cashout in less than y days.
        if post_age > timedelta(days=days_old) \
                and post_cashout_time_remaining < timedelta(days=days_before_cashout) \
                and post_cashout_time_remaining > timedelta(days=0):

            post_pending_payout_value = post['pending_payout_value']

            # insert match data as single row into DataFrame
            post_data_row = {
                'id': str(match_count),
                'author': post_author,
                'permlink': post_permlink,
                'pending_value_hbd': float(post_pending_payout_value.split(' ')[0]),
                'remaining_time_until_cashout': str(post_cashout_time_remaining),
                'voted': post_voted
            }

            # posts_filtered_df.loc[len(posts_filtered_df)] = post_data_row
            posts_filtered_df = posts_filtered_df.append(
                post_data_row, ignore_index=True)

            # insert to return list
            posts_filtered.append(post_data_row)
            match_count += 1
        else:
            # go to next loop
            continue

    print(f'{len(posts_filtered)} posts match found within {post_search_limit} post searches.\n')

    # set index to id column
    posts_filtered_df.set_index('id', inplace=True)
    # sort by hbd value & remaining time then print DataFrame as string
    print(posts_filtered_df.sort_values(
        by=['pending_value_hbd', 'remaining_time_until_cashout'],
        ascending=[False, False]).to_string())
    print('\n')
    # sort and return posts_filtered
    posts_filtered_sorted = sorted(
        posts_filtered, key=lambda item: item.get('pending_value_hbd'), reverse=True)
    return posts_filtered_sorted


def main():
    start = time.time()
    # max limit = 100, otherwise api request will returns error
    get_posts_in_age_range(voter=None, target_tag="leofinance",
                           days_old=2, days_before_cashout=6, limit=100)
    end = time.time()
    time_consumed = end - start
    print(f'\nThis search took {time_consumed:.2f} seconds.')


if __name__ == "__main__":
    main()
