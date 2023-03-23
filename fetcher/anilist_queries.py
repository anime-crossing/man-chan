class AnilistQueries:
    media = """
    query ($id: Int){
        Media(id: $id){
            title{
                romaji
            }
            type
            format
            status
            description
            episodes
            coverImage {
                extraLarge
            }
            siteUrl
            averageScore
            genres
            startDate {
                year
                month
                day
            }
            endDate {
                year
                month
                day
            }
            chapters
            volumes
        }
    }
    """
    score = """
    query ($user: Int, $id: Int){
        MediaList(userId: $user, mediaId: $id){
            user{
                name
            }
            score(format: POINT_10_DECIMAL)
            status
            progress
        }
    }
    """
    account = """
    query ($name: String){
        User(name: $name){
            id
            name
            avatar{
                large
            }
            siteUrl
        }
    }
    """
    search = """
    query ($type: MediaType, $format: MediaFormat, $page: Int, $perPage: Int, $search: String) {
        Page(page: $page, perPage: $perPage) {
            pageInfo {
                total
                currentPage
                lastPage
                hasNextPage
                perPage
            }
            media(search: $search, type: $type, format: $format) {
                id
                title {
                    romaji
                }
                studios(isMain: true) {
                    nodes {
                        name
                    }
                }
                staff(perPage: 2){
                    edges{
                        role
                    }
                    nodes{
                        name {
                            full
                        }
                    }
                }
                popularity
            }
        }
    }
    """
    leaderboard = """
    query($id: Int){
        User(id: $id){
            statistics{
                anime{
                    minutesWatched
                    chaptersRead
                }
            }
        }
    }
    """
