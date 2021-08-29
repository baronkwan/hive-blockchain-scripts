# hive_blockchain_scripts
Set of helpful scripts made to interact with the HIVE blockchain.

## Python modules and libraries used
```
pandas - for data manipulation
requests - for online data retrieval and API calls
datetime - for date formatting and convertion
beem - for HIVE blockchain interaction
```

## What is HIVE?
Hive is an innovative and forward-looking decentralized blockchain and ecosystem, designed to scale with widespread adoption of the currency and platforms in mind. By combining the lightning-fast processing times and fee-less transactions, Hive is positioned to become one of the leading Web3 blockchains used by people around the world.

 (https://hive.io/)

---

## Scripts under this repo:

  Run individually:
  
    - get_posts_in_age_range.py
    
  Require credentials.json:
  
    - target_tag_vote.py


---
    
## credentials.json format:

```
{
  "accounts": [
    {
      "account_name": "HIVE_ACCOUNT_NAME1",
      "wif_posting_key": "5XXXXXXX"
    },
    {
      "account_name": "HIVE_ACCOUNT_NAME2",
      "wif_posting_key": "5XXXXXXX"
    }
  ]
}

```

---
    
## Script description:

### get_posts_in_age_range.py

```Objective: To get post searchs for user defined tag in user defined date range through the hive.blog condenser API.```

```Return value: print out a pandas DataFrame and return an user-defined array in descending order of pending_value_hbd.```

CMD print result:

![image](https://user-images.githubusercontent.com/15119515/131226190-8f9c5083-3025-49b1-8c77-ee7321ca49f3.png)

---

### target_tag_vote.py

```Objective: To submit vote operation to HIVE blockchain when the voter VP & RC are in good condition.```

```Return value: None. Action submitted to the HIVE blockchain.```
