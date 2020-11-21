import json
import flask
from flask import request, jsonify

data_file = 'data.json'

# init
app = flask.Flask(__name__)
app.config["DEBUG"] = True
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True

with open(data_file) as jfile:
    data = json.load(jfile)



# API functions
@app.route('/', methods=['GET'])
def home():
    return "<h1>Pokedex API Home</h1>"



@app.route('/list', methods=['GET'])
def filter_by_type():
    """
        Used to list pokemons by type. Can also sort by certain attributes.

        Usage:
            Filter:
                <url>/list?type=<param>
            Sort:
                <url>/list?sortby=<param>
            Filter and Sort:
                <url>/list?type=<param1>&sortby=<param2>
    """
    type = request.args.get('type')
    sort = request.args.get('sortby')
    result = []
    if(type):
        filtered_list = filter(lambda pokemon: type_checker(type.capitalize(), pokemon), data['pokemons'])
        for pokemon in filtered_list:
            result.append(pokemon)
    else:
        result = data['pokemons']
        
    if(sort):
        result.sort(key=lambda pokemon: pokemon[sort.capitalize()])
    
    return jsonify(result)


@app.route('/list', methods=['GET'])
def list_pokemon():
    """
        Lists all pokemon.

        Usage:
            <url>/list
    """
    return jsonify(data['pokemons'])



@app.route('/list/<category>', methods=['GET'])
def list(category):
    """
        Used to list types, moves, or pokemon.

        Usage:
            <url>/list/<category>
    """
    return jsonify(data[category])



@app.route('/get/<name>', methods=['GET'])
def get_by_name(name):
    """
        Used to get a specific pokemon, type, or move by its name.

        Usage:
            <url>/get/<name>
    """
    result = get_pokemon_by_name(name)
    if(result):
        return jsonify(result)
    result = get_type(name)
    if(result):
        return jsonify(result)
    result = get_move(name)
    if(result):
        return jsonify(result)



@app.route('/get', methods=['GET'])
def get_func():
    """
        Used to get the pokemon with the min or max value regarding the given feature.

        Usage:
            <url>/get?func=<param1>&feature=<param2>
    """
    func = request.args.get('func')
    feature = request.args.get('feature')
    if(func):
        feature_dict = {}
        if(feature):
            if(feature.lower()=='weight'):
                for pokemon in data['pokemons']:
                    feature_dict[pokemon['Name']] = format_weight(pokemon['Weight'])

            elif(feature.lower()=='height'):
                for pokemon in data['pokemons']:
                    feature_dict[pokemon['Name']] = format_height(pokemon['Height'])
            else:
            	for pokemon in data['pokemons']:
            		feature_dict[pokemon['Name']] = float(pokemon[feature])
            if(func.lower() == 'max'):
                return get_pokemon_by_name(max(feature_dict, key=feature_dict.get))
            if(func.lower() == 'min'):
                return get_pokemon_by_name(min(feature_dict, key=feature_dict.get))
    return "Error"



@app.route('/count', methods=['GET'])
def count():
    """
        Used to get the number of moves a pokemon has.

        Usage:
        	<url>/count?pokemon=<param>
    """
    pokemon_name = request.args.get('pokemon')
    if(pokemon_name):
        pokemon = get_pokemon_by_name(pokemon_name)
        if(pokemon):
            return jsonify(count_moves(pokemon))



# helper functions
def type_checker(type, pokemon):
    secondary_type = False
    if('Type II' in pokemon):
        secondary_type = (pokemon['Type II'] == [type])
    if('Next evolution(s)' in pokemon):
        for evolution in pokemon['Next evolution(s)']:
            secondary_type = secondary_type or type_checker(type, get_pokemon_by_name(evolution['Name']))
    return (pokemon['Type I'] == [type] or secondary_type)

def get_pokemon_by_name(name):
    try:
        return next(filter(lambda pokemon: pokemon['Name'] == name, data['pokemons']))
    except StopIteration as e:
        return None

def get_type(name):
    try:
        return next(filter(lambda type: type['name'] == name, data['types']))
    except StopIteration as e:
        return None

def get_move(name):
    try:
        return next(filter(lambda move: move['name'] == name, data['moves']))
    except StopIteration as e:
        return None


def format_weight(weight):
    return float(weight.replace(',','.',1)[:-3])

def format_height(height):
    return float(height.replace(',','.',1)[:-2])


def count_moves(pokemon):
    return len(pokemon['Fast Attack(s)']) + len(pokemon['Special Attack(s)'])


        
app.run()
