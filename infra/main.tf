terraform {
    required_providers {
        aws = {
        source  = "hashicorp/aws"
        version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = "ap-northeast-1"
}


# ───── Users ─────
resource "aws_dynamodb_table" "users" {
    name         = "Users"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "user_id"

    attribute { 
        name = "user_id"
        type = "S" 
    }

    attribute { 
        name = "username"
        type = "S" 
    }

    attribute { 
        name = "email"
        type = "S" 
    }

    global_secondary_index {
        name            = "UsernameIndex"
        hash_key        = "username"
        projection_type = "ALL"
    }
    global_secondary_index {
        name            = "EmailIndex"
        hash_key        = "email"
        projection_type = "ALL"
    }
}

# ───── Tweets ─────
resource "aws_dynamodb_table" "tweets" {
    name         = "Tweets"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "tweet_id"
    range_key    = "created_at"

    attribute { 
        name = "tweet_id"
        type = "S"
        }

    attribute { 
        name = "created_at"
        type = "S"
        }

    attribute { 
        name = "user_id"
        type = "S"
        }

    attribute { 
        name = "username"
        type = "S"
        }
    
    global_secondary_index {
        name            = "ByUser"
        hash_key        = "user_id"
        range_key       = "created_at"
        projection_type = "ALL"
    }

    global_secondary_index {
        name            = "ByUsername"
        hash_key        = "username"
        range_key       = "created_at"
        projection_type = "ALL"
    }
}


# ───── Follows ─────
resource "aws_dynamodb_table" "follows" {
    name         = "Follows"
    billing_mode = "PAY_PER_REQUEST"
    hash_key     = "follow_id"
    range_key    = "created_at"

    attribute { 
        name = "follow_id"
        type = "S"
        }

    attribute { 
        name = "follower_username"
        type = "S"
        }

    attribute { 
        name = "following_username"
        type = "S"
        }

    attribute { 
        name = "created_at"
        type = "S"
        }
    
    global_secondary_index {
        name            = "ByFollowerUser"
        hash_key        = "follower_username"
        range_key       = "created_at"
        projection_type = "ALL"
    }

    global_secondary_index {
        name            = "ByFollowingUser"
        hash_key        = "following_username"
        range_key       = "created_at"
        projection_type = "ALL"
    }
}
