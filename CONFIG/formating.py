import json


async def format_json_f(str_) -> dict:
    return json.loads(str_)
    
    
async def format_json(dicter):
    return json.dumps(dicter)

async def format_for_str(dicter) -> str:
    new_str = '📊Статиситка📊\n'
    i = 1
    for key, value in dicter.items():
        new_str += f'   {i}. {key}: {value}\n'
        i += 1
    return new_str

async def get_dicter(dicter: dict) -> dict:
    new_dict = {'descr': dicter['data_poll']['question'], 
                'variants': json.dumps(dicter['data_poll']['options']), 
                'multiple_choice': dicter['data_poll']['multiple'],
                'url': dicter['url'],
                'topic_name': dicter['topics'],
                'max_vote': dicter['max_vote']}
    return new_dict


if __name__ == '__main__':
    asyncio.run(get_diicter(a))