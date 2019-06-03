import pickle
import room_generator


# def describe_room(room):
#     return 'You see an average-sized room. It\'s pretty empty.'

FILENAME = 'state.pickle'


class Game:
    def __init__(self):
        try:
            pickle_in = open(FILENAME, 'rb')
            state = pickle.load(pickle_in)
            if state['exit'] is not None:
                self.room = room_generator.generate_consecutive_room(state['exit'], state['room'])
                self.hero_path = None
                self.action = 'You enter the room.'
            else:
                self.room = state['room']
                self.hero_path = state['hero_path']
                self.action = state['action']

            self.exit = None
        except FileNotFoundError:
            self.room = room_generator.generate_room_from_scratch()
            self.hero_path = None
            self.action = 'You descend the stairs.'
            self.exit = None

    def step(self):
        if self.hero_path is None:
            self.hero_path = room_generator.generate_path(self.room)
        elif len(self.hero_path) == 2:
            room_generator.open_door(self.hero_path[1], self.room)
            self.action = 'You open the door. It leads to the next room.'
            self.exit = self.hero_path[1]
        else:
            self.action = f'You move {room_generator.move_hero(self.hero_path, self.room)}.'
        self.save_state()

    def save_state(self):
        pickle_out = open(FILENAME, 'wb')
        pickle.dump({
            'room': self.room,
            'hero_path': self.hero_path,
            'action': self.action,
            'exit': self.exit
        }, pickle_out)
        pickle_out.close()

    def ascii_snapshot(self):
        return room_generator.to_ascii(self.room) + '\n' + self.action
