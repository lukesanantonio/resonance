# Credit to Matt

# user_songs maps (user) IDs to a list of top artists (in the form of Spotify
# IDs).

# Issue with implementation: This only works while we deal with Spotify. It
# could work if we allow the user to select artists themselves, and just query
# their ID (in addition to making sure the artist exists).

class MatchInfo:
    def __init__(self, id, name, like_score, unlike_score, artists):
        self.id = id
        self.name = name
        self.like_score = like_score
        self.unlike_score = unlike_score
        self.artists = artists

def match(user_songs, cur_user_id):

    like_scores = {}
    unlike_scores = {}
    shared_artists = {}

    # We can't match with a user that doesn't have any songs
    if cur_user_id not in user_songs:
        return [], False

    for their_user_id, top_artists in user_songs.items():
        # We don't want to match the user with himself, that might get
        # depressing.
        if their_user_id == cur_user_id: continue

        # Now we have two different users

        like_score = 0
        unlike_score = 0

        for our_song_i, our_song in enumerate(user_songs[cur_user_id]):
            for their_song_i, their_song in enumerate(user_songs[their_user_id]):
                if our_song == their_song:
                    like_score += abs(our_song_i - their_song_i)

                    # Add the song to the list of matches
                    if their_user_id not in shared_artists:
                        shared_artists[their_user_id] = []

                    shared_artists[their_user_id].append(our_song)
                else:
                    unlike_score += 1

        # Link the match score that *this* user had with the *current* user.
        like_scores[their_user_id] = like_score
        unlike_scores[their_user_id] = unlike_score

    like_list = [(id, score) for id, score in like_scores.items()]
    unlike_list = [(id, score) for id, score in unlike_scores.items()]

    # Sort by the like list by score
    sorted_user_pairs = sorted(like_list, key=lambda tup: tup[1])

    # Final matches is an array of user ids
    final_matches = []

    # We don't want to match the user with himself, that might get depressing
    # Check to see if like score is zero, if it is we may have to remove
    # that user depending on the value of unlike list
    for matched_id, like_score in sorted_user_pairs:
        unlike_score = unlike_scores[matched_id]
        if like_score == 0 and unlike_score == 2500:
            # These users might as well kill each other. When the unlike
            # score is equal to 2500 then that means that there is no match
            # and that user should be taken off the list of suggested
            # friends.
            pass
        else:
            match = MatchInfo(matched_id, '', like_score, unlike_score,
                              shared_artists[matched_id])
            final_matches.append(match)

    return final_matches, True
