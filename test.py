import poker
if __name__ == '__main__':
    cards=['♧2','♡K', '♡A', '♧10']
    print(poker.get_point_sum(cards))
    cards.remove('♧9')
    print(cards)