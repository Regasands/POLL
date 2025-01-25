import json


async def format_json_f(str_) -> dict:
    return json.loads(str_)
    
    
async def format_json(dicter):
    return json.dumps(dicter)


async def format_for_str(dicter, arg_1, arg_2) -> str:
    new_str = '📊 **Статистика** 📊\n\n'
    i = 1
    for key, value in dicter.items():
        new_str += f'🔹 {i}. {key}: {value}\n'
        i += 1
    new_str += f'\n🔘 Кол-во проголосовавших: {arg_1}\n'
    new_str += f'🔘 Кол-во оставшихся голосов: {arg_2 - arg_1}\n'
    new_str += '\nСпасибо за использование! 😊'
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