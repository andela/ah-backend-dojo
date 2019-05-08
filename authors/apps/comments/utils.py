from rest_framework import response, status

def validateData(end_index,start_index, article):

    if type(end_index) != int or type(start_index) != int:
        return response.Response(
            {
            "error": "Make sure the start_index and end_index are integers."
            },
            status.HTTP_400_BAD_REQUEST
        )

    if (start_index > len(article.body)) and (end_index > len(article.body)):
        return response.Response(
            {
                "error": "Start_index or end_index is out of index."
            },
            status.HTTP_400_BAD_REQUEST
        )

    if start_index < end_index:
        return True
    return response.Response(
        {
         "error": "start_index should be less than end_index."
        },
        status.HTTP_400_BAD_REQUEST
    )