import pickle
from room_generator import Wall
import room_generator
import random


FILENAME = 'state.pickle'


class Game:
    def __init__(self):
        generator = random.Random()
        try:
            pickle_in = open(FILENAME, 'rb')
            state = pickle.load(pickle_in)

            # use saved info to continue journey inside current room
            # remove after first run
            if 'generator_state' in state:
                self.generator_state = state['generator_state']
            else:
                self.generator_state = generator.getstate()

            if state['exit'] is None:
                generator.setstate(self.generator_state)
                self.room = state['room']
                self.hero_path = state['hero_path']
                self.action = state['action']
            else:
                generator.setstate(self.generator_state)
                # remove after first run
                if type(state['exit']) == room_generator.Position:
                    entrance = Wall.from_room_position(state['exit'], state['room'])
                    entrance = Wall.opposite_wall(entrance)
                else:
                    entrance = Wall.opposite_wall(state['exit'])
                self.room = room_generator.generate_consecutive_room(entrance, generator)
                room_generator.place_hero_near_the_door(self.room, generator)
                self.hero_path = None
                self.action = 'You enter the room.'
        except FileNotFoundError:
            self.generator_state = generator.getstate()
            self.room = room_generator.generate_room_from_scratch(generator)
            room_generator.place_hero_near_the_stairs(self.room, generator)
            self.hero_path = None
            self.action = 'You descend the stairs.'

        self.generator = generator
        self.exit = None

    def step(self):
        if self.hero_path is None:
            self.hero_path = room_generator.generate_path(self.room, self.generator)
        elif len(self.hero_path) == 2:
            room_generator.open_door(self.hero_path[1], self.room)
            self.action = 'You open the door. It leads to the next room.'
            self.exit = Wall.from_room_position(self.hero_path[1], self.room)
        else:
            self.action = f'You move {room_generator.move_hero(self.hero_path, self.room)}.'
        self.save_state()

    def save_state(self):
        pickle_out = open(FILENAME, 'wb')
        pickle.dump({
            'generator_state': self.generator.getstate(),
            'room': self.room,
            'hero_path': self.hero_path,
            'action': self.action,
            'exit': self.exit
        }, pickle_out)
        pickle_out.close()

    def ascii_snapshot(self):
        return room_generator.to_ascii(self.room) + '\n' + self.action
