from database import (
    create_friend_request,
    create_friendship,
    create_message,
    get_conversation_messages,
    get_friends_list,
    get_friend_request_by_id,
    get_friendship,
    get_incoming_friend_requests,
    get_outgoing_friend_requests,
    get_pending_friend_request_between,
    get_user_by_id,
    search_student_directory,
    update_friend_request_status,
)


class SocialService:
    def search_students(self, current_user_id, query):
        query = query.strip()
        if not query:
            return []

        # Enrich directory results with relationship status so the view can stay simple.
        students = search_student_directory(query, exclude_user_id=current_user_id)
        friend_ids = {friend["id"] for friend in get_friends_list(current_user_id)}
        incoming_ids = {request["sender_id"] for request in get_incoming_friend_requests(current_user_id)}
        outgoing_ids = {request["receiver_id"] for request in get_outgoing_friend_requests(current_user_id)}

        enriched = []
        for student in students:
            candidate = dict(student)
            if candidate["id"] in friend_ids:
                candidate["relationship_status"] = "friends"
            elif candidate["id"] in incoming_ids:
                candidate["relationship_status"] = "incoming_request"
            elif candidate["id"] in outgoing_ids:
                candidate["relationship_status"] = "outgoing_request"
            else:
                candidate["relationship_status"] = "none"
            enriched.append(candidate)
        return enriched

    def get_dashboard_data(self, user_id):
        return {
            "incoming_requests": get_incoming_friend_requests(user_id),
            "friends": get_friends_list(user_id),
        }

    def send_friend_request(self, sender_id, receiver_id):
        if sender_id == receiver_id:
            return {"success": False, "message": "You cannot send a friend request to yourself."}

        receiver = get_user_by_id(receiver_id)
        if not receiver or receiver.get("user_role") != "Student":
            return {"success": False, "message": "Selected student could not be found."}
        if receiver.get("status") != "Approved":
            return {"success": False, "message": "This student is not available for friend requests yet."}

        if get_friendship(sender_id, receiver_id):
            return {"success": False, "message": "You are already friends with this student."}

        pending_request = get_pending_friend_request_between(sender_id, receiver_id)
        if pending_request:
            if pending_request["sender_id"] == sender_id:
                return {"success": False, "message": "You already sent a friend request to this student."}
            return {"success": False, "message": "This student already sent you a friend request. Accept it from the requests panel."}

        request_id = create_friend_request(sender_id, receiver_id)
        if not request_id:
            return {"success": False, "message": "Could not send the friend request right now."}

        return {"success": True, "message": "Friend request sent!", "request_id": request_id}

    def respond_to_friend_request(self, user_id, request_id, action):
        request = get_friend_request_by_id(request_id)
        if not request or request.get("receiver_id") != user_id:
            return {"success": False, "message": "Friend request not found."}
        if request.get("status") != "pending":
            return {"success": False, "message": "This friend request has already been handled."}

        if action == "accept":
            if not get_friendship(request["sender_id"], request["receiver_id"]):
                if not create_friendship(request["sender_id"], request["receiver_id"]):
                    return {"success": False, "message": "Could not add this student to your friends list."}
            if not update_friend_request_status(request_id, "accepted"):
                return {"success": False, "message": "Could not accept the friend request."}
            return {"success": True, "message": "Friend request accepted!"}

        if action == "reject":
            if not update_friend_request_status(request_id, "rejected"):
                return {"success": False, "message": "Could not reject the friend request."}
            return {"success": True, "message": "Friend request rejected."}

        return {"success": False, "message": "Invalid friend request action."}

    def get_friends_list(self, user_id):
        return get_friends_list(user_id)

    def get_conversation(self, user_id, friend_id):
        friend = get_user_by_id(friend_id)
        if not friend or friend.get("user_role") != "Student":
            return {"success": False, "message": "Friend not found."}
        if not get_friendship(user_id, friend_id):
            return {"success": False, "message": "You can only chat with accepted friends."}

        return {
            "success": True,
            "friend": friend,
            "messages": get_conversation_messages(user_id, friend_id),
        }

    def send_message(self, sender_id, receiver_id, message_text):
        clean_message = message_text.strip()
        if not clean_message:
            return {"success": False, "message": "Message cannot be empty."}

        # Only accepted friends are allowed to exchange messages.
        if not get_friendship(sender_id, receiver_id):
            return {"success": False, "message": "You can only message students who are already your friends."}

        message_id = create_message(sender_id, receiver_id, clean_message)
        if not message_id:
            return {"success": False, "message": "Message failed to send."}

        return {"success": True, "message": "Message sent!", "message_id": message_id}
