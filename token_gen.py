import hashlib
import base64

# The user id will be inferred from the currently logged in user. If no one's
# currently logged in we can prompt them to do that.

def make_download_token(song, user):
    """Creates a single token that describes a song to download by one user."""
    hash_gen = hashlib.sha256()

    # Combine the song hash, and user_id then hash that.
    # We are not using a timestamp since for now we'll just allow the user to
    # download any song they own given they are logged in, the point of the
    # token is give an id to a song-user pair (for redis). This means a user
    # couldn't download another user's song for example.
    hash_gen.update(song)
    hash_gen.update(str(user).encode('utf-8'))

    # Use 32 since it's case insensitive!
    token = base64.b32encode(hash_gen.digest())

    return token.decode('utf-8')

def verify_download_token(token, song, user):
    hash_gen = hashlib.sha256()

    hash_gen.update(song)
    hash_gen.update(str(user).encode('utf-8'))

    # For now, only accept uppercase letters. We can always make it case
    # *insensitive* if it becomes an issue by adding the parameter:
    # casefold=True
    binrep = base64.b32decode(token)

    return binrep == hash_gen.digest()
