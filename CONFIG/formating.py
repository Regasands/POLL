import json


async def format_json_f(self, str_) -> dict:
    return json.loads(str_)

async def get_dicter(dicter: dict) -> dict:
    new_dict = {'descr': dicter['data_pull']['question'], 
                'variants': json.dumps({i: 0 for i in dicter['data_pull']['options']}), 
                'multiple_choice': dicter['data_pull']['multiple'],
                'url': dicter['url'],
                'topic_name': dicter['topics'],
                'max_vote': dicter['max_vote']}
    return new_dict


if __name__ == '__main__':
    asyncio.run(get_diicter(a))