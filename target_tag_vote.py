from beem import Hive
from beem.steem import Steem
from beembase import operations
from beem.transactionbuilder import TransactionBuilder
import requests
import time
import json
from datetime import datetime
from get_posts_in_age_range import get_posts_in_age_range
import sys
import os
from pprint import pprint

# TODO Add argparse functionality for CMD use
# import argparse
# parser = argparse.ArgumentParser()
# parser.add_argument("")
# args = parser.parse_args()

nodes = ['https://anyx.io/', 'https://api.hive.blog',
         "https://api.deathwing.me"]


class HiveRequests:
    def __init__(self, private_posting_key):
        self.s = Steem(node=nodes[2], keys=[private_posting_key])
        self.s.chain_params['chain_id'] = 'beeab0de00000000000000000000000000000000000000000000000000000000'

    def post_vote(self, author, permlink, weight=10000):
        try:
            author = author
            permlink = permlink
            print(f'Voting on @{author}/{permlink} with {weight/100}%.')
            # build tx for vote on permlink
            op = operations.Vote(**{
                "voter": voter,
                "author": author,
                "permlink": permlink,
                "weight": weight
            })
            tx = TransactionBuilder(blockchain_instance=self.s)
            tx.appendOps(op)
            tx.appendSigner(voter, "posting")
            tx.sign()
            broadcast = tx.broadcast()
            print(f'Successfully voted @{author}/{permlink}.')
            pprint(broadcast)
            time.sleep(3)
        except Exception as e:
            try:
                format_exception_error()
            except:
                pass


def get_vp(voter):
    """get_vp: get voter's current voting power on Hive blockchain."""
    data_vp = {
        "jsonrpc": "2.0",
        "method": "condenser_api.get_accounts",
        "params": [[voter]],
        "id": 1
    }
    r_vp = requests.post(nodes[0], json=data_vp)
    result_vp = r_vp.json()['result'][0]

    vesting_shares = float(result_vp['vesting_shares'].split()[0])
    received_vesting_shares = float(
        result_vp['received_vesting_shares'].split()[0])
    delegated_vesting_shares = float(
        result_vp['delegated_vesting_shares'].split()[0])
    vesting_withdraw_rate = float(
        result_vp['vesting_withdraw_rate'].split()[0])
    total_shares = vesting_shares + received_vesting_shares - \
        delegated_vesting_shares - vesting_withdraw_rate

    last_update_time = float(result_vp['voting_manabar']['last_update_time'])
    elasped_time = datetime.timestamp(datetime.now()) - last_update_time
    max_mana = total_shares * 1000000
    # 5 days (=432000 seconds) until mana fully recharged
    current_mana = float(
        result_vp['voting_manabar']['current_mana']) + elasped_time * max_mana/432000

    if current_mana > max_mana:
        current_mana = max_mana

    vp = round(current_mana * 100 / max_mana)
    print(f'\n[{voter}] current VP: {vp}')
    return vp


def get_rc(voter):
    """get_rc: get voter's current resources credit on Hive blockchain.
    """
    data_rc = {
        "jsonrpc": "2.0",
        "method": "rc_api.find_rc_accounts",
        "params": {"accounts": [voter]},
        "id": 1
    }
    r_rc = requests.post(nodes[0], json=data_rc)
    rc = r_rc.json()["result"]["rc_accounts"]

    max_rc = float(rc[0]["max_rc"])
    rc_manabar = float(rc[0]["rc_manabar"]["current_mana"])
    rc = int((rc_manabar / max_rc) * 100)
    print(f'[{voter}] current RC: {rc}')
    return rc


def format_exception_error():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    print(exc_type, fname, exc_tb.tb_lineno)


def main(voter, wif_posting_key):

    r = HiveRequests(wif_posting_key)

    vp = get_vp(voter)
    rc = get_rc(voter)

    # check if vp and rc in range
    if vp >= 80 and rc >= 50:
        vote_count = 0
        # get posts
        posts_filtered = get_posts_in_age_range(
            voter=voter, target_tag="leofinance", days_old=2, days_before_cashout=6)
        # Only selecting the top 10 posts to vote
        for post in posts_filtered[:10]:
            author = post['author']
            permlink = post['permlink']
            voted = post['voted']

            if voted:
                print(f'This post had already voted by {voter}.')
                continue

            print(f'\n{voter} start voting')
            r.post_vote(author, permlink)
            vote_count += 1

        print(f'#{vote_count} posts voted.\n')

    else:
        print(f'\nAccount VP: < 80 or RC: < 50, please wait until recharged.')


if __name__ == "__main__":
    start = time.time()

    with open('credentials.json', 'r') as file:
        credentials = json.loads(file.read())

    for i in credentials['accounts']:
        voter = i['account_name']
        wif_posting_key = i['wif_posting_key']

        main(voter, wif_posting_key)

    end = time.time()
    time_used = end - start
    print(f'\nTime used: {time_used:.2f} seconds.')
