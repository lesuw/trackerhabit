from .models import MessageVote

def user_votes(request):
    if request.user.is_authenticated:
        votes = MessageVote.objects.filter(user=request.user).values_list('message_id', 'vote')
        user_votes_dict = {message_id: vote for message_id, vote in votes}
        return {'user_votes': user_votes_dict}
    return {'user_votes': {}}