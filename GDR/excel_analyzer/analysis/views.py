import pandas as pd
import os
import json
from django.http import JsonResponse
from django.shortcuts import render


# Convert Excel to JSON
def convert_excel_to_json(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  
    output_json_path = os.path.join(os.path.dirname(file_path), "data.json")

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Convert datetime columns to string format
    for col in df.select_dtypes(include=['datetime64[ns]']).columns:
        df[col] = df[col].astype(str)

    # Convert to JSON and save it
    json_data = df.to_dict(orient="records")  
    with open(output_json_path, "w", encoding="utf-8") as json_file:
        json.dump(json_data, json_file, indent=4, ensure_ascii=False)

    # Print the first 60 rows for verification
    first_60_rows = df.head(60).to_dict(orient="records")

    return JsonResponse({"message": "JSON file created successfully!", "preview": first_60_rows})


# Function to calculate percentage of voice chat matches per day
def voice_game_percentage(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")

    # Remove rows with missing dates
    df = df.dropna(subset=["EVENTDATE"])

    # Convert ISVOICEGAME column to numeric (handling missing values)
    df["ISVOICEGAME"] = pd.to_numeric(df["ISVOICEGAME"], errors="coerce").fillna(0)

    # Group by date
    daily_counts = df.groupby(df["EVENTDATE"].dt.date).agg(
        total_users=("USERID", "count"),
        voice_game_users=("ISVOICEGAME", "sum")
    )

    # Calculate percentage
    daily_counts["percentage_voice_games"] = (
        daily_counts["voice_game_users"] / daily_counts["total_users"]
    ) * 100

    # Convert to records and format dates as strings
    result = daily_counts.reset_index().to_dict(orient="records")
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"percentage_voice_games_per_day": result})
    
    # Otherwise render the template
    return render(request, 'analysis/voice_game_stats.html', {'stats': result})


# Add this new view function
def landing_page(request):
    return render(request, 'analysis/landing_page.html')


def match_type_analysis(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")

    # Group by user and date, count unique match types
    daily_user_matches = df.groupby([df["EVENTDATE"].dt.date, "USERID"])["MATCHTYPE"].nunique().reset_index()
    
    # Filter users who played at least 2 match types
    users_multiple_matches = daily_user_matches[daily_user_matches["MATCHTYPE"] >= 2]
    
    # Count number of such users per day
    result = users_multiple_matches.groupby("EVENTDATE").size().reset_index()
    result.columns = ["date", "users_count"]
    
    # Convert to records
    result_data = result.to_dict(orient="records")
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"users_multiple_matchtypes": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/match_type_stats.html', {'stats': result_data})


def voice_chat_frequency(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")
    
    # Convert ISVOICEGAME column to numeric (handling missing values)
    df["ISVOICEGAME"] = pd.to_numeric(df["ISVOICEGAME"], errors="coerce").fillna(0)
    
    # Group by date and user, count voice chat matches
    user_daily_voice = df[df["ISVOICEGAME"] == 1].groupby(
        [df["EVENTDATE"].dt.date, "USERID"]
    ).size().reset_index(name="voice_matches")
    
    # Calculate average voice matches per user per day
    daily_average = user_daily_voice.groupby("EVENTDATE").agg(
        avg_voice_matches=("voice_matches", "mean"),
        total_users=("USERID", "count")
    ).reset_index()
    
    # Round to 2 decimal places
    daily_average["avg_voice_matches"] = daily_average["avg_voice_matches"].round(2)
    
    # Convert to records
    result_data = daily_average.to_dict(orient="records")
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"voice_chat_frequency": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/voice_chat_frequency.html', {'stats': result_data})


def most_regular_matchtype(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)
    
    # Debug prints
    print("\nUnique MATCHTYPE values:", df["MATCHTYPE"].unique())
    
    # Filter for actual match events (not queue events)
    match_events = df[df["EVENTNAME"].isin(["matchStarted", "matchWon", "matchLost"])]
    
    # Group by user and matchtype, count matches
    user_matchtype_counts = match_events.groupby(['USERID', 'MATCHTYPE']).size().reset_index(name='match_count')
    
    # For each user, find their most played matchtype
    user_preferred = user_matchtype_counts.loc[user_matchtype_counts.groupby('USERID')['match_count'].idxmax()]
    
    # Aggregate statistics by matchtype
    matchtype_summary = user_preferred.groupby('MATCHTYPE').agg(
        user_count=('USERID', 'count'),  # Number of users who prefer this type
        avg_matches=('match_count', 'mean')  # Average matches for users who prefer this type
    ).reset_index()
    
    # Sort by number of users in descending order
    matchtype_summary = matchtype_summary.sort_values('user_count', ascending=False)
    
    # Round average matches
    matchtype_summary['avg_matches'] = matchtype_summary['avg_matches'].round(2)
    
    # Add total matches per type
    total_matches_per_type = match_events.groupby('MATCHTYPE').size().reset_index(name='total_matches')
    matchtype_summary = matchtype_summary.merge(total_matches_per_type, on='MATCHTYPE', how='left')
    
    # Convert to records
    result_data = matchtype_summary.to_dict(orient="records")
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"most_regular_matchtype": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/most_regular_matchtype.html', {'stats': result_data})


def voice_chat_streak(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")
    
    # Convert ISVOICEGAME column to numeric (handling missing values)
    df["ISVOICEGAME"] = pd.to_numeric(df["ISVOICEGAME"], errors="coerce").fillna(0)
    
    # Filter for voice chat matches and get unique dates per user
    voice_chat_dates = df[df["ISVOICEGAME"] == 1].groupby("USERID")["EVENTDATE"].apply(
        lambda x: sorted(list(x.dt.date.unique()))
    )
    
    def calculate_streak(dates):
        if not dates:
            return 0
        
        max_streak = current_streak = 1
        for i in range(1, len(dates)):
            # Check if dates are consecutive
            if (dates[i] - dates[i-1]).days == 1:
                current_streak += 1
                max_streak = max(max_streak, current_streak)
            else:
                current_streak = 1
        return max_streak
    
    # Calculate streak for each user
    user_streaks = voice_chat_dates.apply(calculate_streak)
    
    # Get top streaks
    top_streaks = user_streaks.sort_values(ascending=False).head(10)
    
    # Prepare results
    result_data = [
        {"user_id": user_id, "max_streak": int(streak)}
        for user_id, streak in top_streaks.items()
    ]
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"voice_chat_streaks": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/voice_chat_streak.html', {'stats': result_data})


def match_completion_rate(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")
    
    # Create a flag for match starts and completions
    match_starts = df[df["EVENTNAME"] == "matchStarted"].groupby(["EVENTDATE", "MATCHID"])["USERID"].first()
    match_ends = df[df["EVENTNAME"].isin(["matchWon", "matchLost"])].groupby(["EVENTDATE", "MATCHID"])["USERID"].first()
    
    # Group by date and calculate completion rate
    daily_stats = pd.DataFrame({
        'matches_started': match_starts.groupby('EVENTDATE').size(),
        'matches_completed': match_ends.groupby('EVENTDATE').size()
    }).fillna(0)
    
    # Calculate completion rate
    daily_stats['completion_rate'] = (daily_stats['matches_completed'] / daily_stats['matches_started'] * 100).round(2)
    
    # Reset index to make EVENTDATE a column
    daily_stats = daily_stats.reset_index()
    
    # Convert to records
    result_data = daily_stats.to_dict(orient="records")
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"match_completion_rates": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/match_completion_rate.html', {'stats': result_data})


def queue_waiting_time(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")
    df["EVENTTIMESTAMP"] = pd.to_datetime(df["EVENTTIMESTAMP"], errors="coerce")
    
    # Filter for matchmaking events
    queue_events = df[
        (df["EVENTNAME"] == "matchmakingQueue") & 
        (df["MATCHMAKINGSTATE"].isin(["started", "matched"]))
    ]
    
    # Sort by user and timestamp
    queue_events = queue_events.sort_values(["USERID", "EVENTTIMESTAMP"])
    
    # Group by user and match to calculate waiting time
    waiting_times = []
    for (user, match), group in queue_events.groupby(["USERID", "MATCHID"]):
        events = group.sort_values("EVENTTIMESTAMP")
        if len(events) >= 2:
            start_time = events[events["MATCHMAKINGSTATE"] == "started"]["EVENTTIMESTAMP"].iloc[0]
            end_time = events[events["MATCHMAKINGSTATE"] == "matched"]["EVENTTIMESTAMP"].iloc[-1]
            waiting_time = (end_time - start_time).total_seconds() / 60  # Convert to minutes
            if waiting_time > 0:  # Only include valid waiting times
                waiting_times.append({
                    "date": events["EVENTDATE"].iloc[0].date(),
                    "waiting_time": waiting_time
                })
    
    # Convert to DataFrame for easier aggregation
    waiting_df = pd.DataFrame(waiting_times)
    
    # Calculate daily statistics
    if not waiting_df.empty:
        daily_stats = waiting_df.groupby("date").agg(
            avg_wait_time=("waiting_time", "mean"),
            min_wait_time=("waiting_time", "min"),
            max_wait_time=("waiting_time", "max"),
            total_matches=("waiting_time", "count")
        ).round(2).reset_index()
        
        # Convert to records
        result_data = daily_stats.to_dict(orient="records")
    else:
        result_data = []
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"queue_waiting_times": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/queue_waiting_time.html', {'stats': result_data})


def queue_cancellation_analysis(request):
    file_path = r"C:\Users\Fares\Desktop\Projects\GDR\excel_analyzer\Data\Data Analyst SQL Assessment.xlsx"  

    # Read the second sheet
    df = pd.read_excel(file_path, sheet_name=1)

    # Debug prints
    print("Available columns:", df.columns.tolist())
    print("\nSample data:")
    print(df.head())
    
    # Check unique values in relevant columns
    print("\nUnique EVENTNAME values:", df["EVENTNAME"].unique())
    print("\nUnique MATCHMAKINGSTATE values:", df["MATCHMAKINGSTATE"].dropna().unique())

    # Ensure EVENTDATE is in proper datetime format
    df["EVENTDATE"] = pd.to_datetime(df["EVENTDATE"], errors="coerce")
    df["EVENTTIMESTAMP"] = pd.to_datetime(df["EVENTTIMESTAMP"], errors="coerce")
    
    # Filter for matchmaking events
    queue_events = df[
        (df["EVENTNAME"] == "matchmakingQueue") & 
        (df["MATCHMAKINGSTATE"].isin(["started", "cancel", "matched"]))
    ]
    
    # Debug print
    print("\nNumber of queue events found:", len(queue_events))
    if len(queue_events) > 0:
        print("\nSample queue event:")
        print(queue_events.iloc[0])
    
    # Group by user and match to identify cancellations
    user_stats = []
    
    for (user, match), group in queue_events.groupby(["USERID", "MATCHID"]):
        events = group.sort_values("EVENTTIMESTAMP")
        
        # Get user profile data from first event
        user_data = {
            "user_id": user,
            "user_level": events["USERLEVEL"].iloc[0] if "USERLEVEL" in events.columns else 0,
            "user_country": events["USERCOUNTRY"].iloc[0] if "USERCOUNTRY" in events.columns else "Unknown",
            "platform": events["PLATFORM"].iloc[0] if "PLATFORM" in events.columns else "Unknown",
            "matchtype": events["MATCHTYPE"].iloc[0] if "MATCHTYPE" in events.columns else "Unknown",
            "time_of_day": events["EVENTTIMESTAMP"].iloc[0].hour,
            "cancelled": "cancel" in events["MATCHMAKINGSTATE"].values
        }
        
        # Calculate wait time before cancel/match
        if len(events) >= 2:
            start_time = events[events["MATCHMAKINGSTATE"] == "started"]["EVENTTIMESTAMP"].iloc[0]
            end_time = events[events["MATCHMAKINGSTATE"].isin(["cancel", "matched"])]["EVENTTIMESTAMP"].iloc[-1]
            user_data["wait_time"] = (end_time - start_time).total_seconds() / 60
        else:
            user_data["wait_time"] = 0
            
        user_stats.append(user_data)
    
    # Convert to DataFrame for analysis
    stats_df = pd.DataFrame(user_stats)
    
    # Initialize empty results
    result_data = {
        "total_users": len(stats_df["user_id"].unique()) if not stats_df.empty else 0,
        "total_queues": len(stats_df) if not stats_df.empty else 0,
        "overall_cancel_rate": stats_df["cancelled"].mean().round(3) if not stats_df.empty else 0,
        "analysis": {}
    }
    
    # Only perform detailed analysis if we have data
    if not stats_df.empty and len(stats_df) > 1:
        # Calculate cancellation rates by different factors
        analysis_results = {}
        
        if "user_level" in stats_df.columns:
            analysis_results["by_level"] = stats_df.groupby(pd.qcut(stats_df["user_level"], q=4))["cancelled"].mean().round(3)
        
        if "user_country" in stats_df.columns:
            analysis_results["by_country"] = stats_df.groupby("user_country")["cancelled"].agg(["mean", "count"]).round(3)
        
        if "platform" in stats_df.columns:
            analysis_results["by_platform"] = stats_df.groupby("platform")["cancelled"].agg(["mean", "count"]).round(3)
        
        if "matchtype" in stats_df.columns:
            analysis_results["by_matchtype"] = stats_df.groupby("matchtype")["cancelled"].agg(["mean", "count"]).round(3)
        
        if "time_of_day" in stats_df.columns:
            analysis_results["by_time"] = stats_df.groupby(pd.qcut(stats_df["time_of_day"], q=4))["cancelled"].mean().round(3)
        
        if "wait_time" in stats_df.columns:
            analysis_results["by_wait_time"] = stats_df.groupby(pd.qcut(stats_df["wait_time"], q=4))["cancelled"].mean().round(3)
        
        # Convert results to records
        result_data["analysis"] = {
            key: df.reset_index().to_dict('records') 
            for key, df in analysis_results.items()
        }
    
    # If JSON is requested, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({"queue_cancellation_analysis": result_data})
    
    # Otherwise render the template
    return render(request, 'analysis/queue_cancellation_analysis.html', {'stats': result_data})
