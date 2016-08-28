# Credit to Matt

if __name__ == '__main__':
    user_list = []
    array_length = 50
    number_of_users = 10

    like_list = []
    unlike_list = []
    for user_i in range(1, number_of_users):
        user_list.append([])

        like_score = 0
        unlike_score = 0

        for our_song_i in range(array_length):
            for their_song_i in range(array_length):
                if user_list[0][our_song_i] == user_list[user_i][their_song_i]:
                    like_score += math.abs(our_song_i - their_song_i)
                else:
                    unlike_score += 1

            like_list.append((user_id, like_score))
            unlike_list.append((user_id, unlike_score))

        sorted_user_pairs = sorted(like_list, key=lamba tup: x[1])

        final_matches = []
        unlike_dict = dict(unlike_list)
        # Check to see if like score is zero, if it is we may have to remove
        # that user depending on the value of unlike list
        for user, like_score in sorted_user_pairs:
            if like_score == 0 and unlike_dict[user_id] == 2500:
                # These users might as well kill each other
            else:
                final_matches.append(user)
