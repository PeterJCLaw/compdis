#!/usr/bin/env python
import redis
import json
import sys
import schedule_finals
import scheduler

"""
Fires a load of test data into redis
"""

SCHEDULED_MATCHES = [
  dict({"time": 0, "teams": ["ARG", "CLF", "CLF2", "BGR"], "delay": 0}),
  dict({"time": 1, "teams": ["CLF", "BWS", "BWS2", "BRK"], "delay": 0}),
  dict({"time": 2, "teams": ["BSG", "EMM", "GRS", "GMR"], "delay": 0}),
  dict({"time": 3, "teams": ["HRS", "HZW", "MFG", "MUC"], "delay": 0}),
  dict({"time": 4, "teams": ["PSC", "PSC2", "QEH", "QMC"], "delay": 0}),
  dict({"time": 5, "teams": ["SEN", "SEN2", "TTN", "QMC"], "delay": 0}),
  dict({"time": 6, "teams": ["BWS", "GRS", "MFG", "QEH"], "delay": 0}),
  dict({"time": 7, "teams": ["BSG", "EMM", "QMC", "SEN"], "delay": 0}),
  dict({"time": 8, "teams": ["SEN2", "CLF", "CLF2", "MUC"], "delay": 0}),
  dict({"time": 9, "teams": ["HRS", "GMR", "GRS", "BRK"], "delay": 0}),
  dict({"time": 10, "teams": ["BGR", "QEH", "EMM", "TTN"], "delay": 0}),
  dict({"time": 11, "teams": ["PSC", "PSC2", "HRW", "QEH"], "delay": 0}),
  dict({"time": 12, "teams": ["EMM", "SEN", "TTN", "MUC"], "delay": 0}),
  dict({"time": 13, "teams": ["QMC", "ARG", "CLF", "CLF2"], "delay": 0}),
  dict({"time": 14, "teams": ["MFG", "QEH", "EMM", "QMC"], "delay": 0}),
  dict({"time": 15, "teams": ["HRS", "HRW", "TTN", "MUC"], "delay": 0}),
  dict({"time": 16, "teams": ["PSC", "RMS", "BGR", "STA"], "delay": 0})]

r = redis.Redis(host='localhost', port=6379, db=0)

WINNING_SCORES = [
    {"tzone": 0, "trobot": 0, "tbucket": 0, "nbuckets": 2}, # 7 tokens
    {"tzone": 0, "trobot": 0, "tbucket": 0, "nbuckets": 2}, # 3 tokens
    {"tzone": 0, "trobot": 0, "tbucket": 0, "nbuckets": 0}, # 7
    {"tzone": 0, "trobot": 0, "tbucket": 0, "nbuckets": 0}] # 3
    
LEAGUE_POINTS = [4, 3, 2, 1]

def WriteScoreForTeam(tla, match_no, zone_no, score, league_points):
    def game_points(score):
      """
      in order, in a list, pass: tzone, trobot, tbucket, nbuckets
      """
      total = 0
      total += int(score[0])
      total += 2*int(score[1])
      total += 5*int(score[2])
      if int(score[3]) > 1:
		    total *= int(score[3])
      return total
	    
    base_var = "org.srobo.scores.match.{0}.{1}".format(match_no, zone_no)
    for key in score:      
      r.hset(base_var, key, score[key]) # please? 
	  
    # now game points
    r.hset(base_var, "game_points", game_points([score["tzone"], score["trobot"], score["tbucket"], score["nbuckets"]]))
    # now league points
    r.hset(base_var, "league_points", league_points)
	  
    # now total league points
    for i in range(league_points):
      r.incr("org.srobo.scores.team." + tla) 
      # incrby doesn't seem to be implemented under that name, lazy 

def CreateFakeResults(teams_drawing = 0):
  """
  Generates scoring data such that the robot in zone 0 comes first and in zone 3 comes last
  in each match, with a sensible distribution of points
  
  Later, draws.
  """      
  for i in range(len(SCHEDULED_MATCHES)):
    for robot in range(4):
      tla = SCHEDULED_MATCHES[i]["teams"][robot]      
      WriteScoreForTeam(tla, i, robot, WINNING_SCORES[robot], LEAGUE_POINTS[robot])

def CreateFakeScoreForMatches(start, end):
  for i in range(start, end):
    match = scheduler.match_from_ms(r.lindex("org.srobo.matches", i))
    
    for robot in range(4):
      WriteScoreForTeam(match["teams"][robot], i, robot, WINNING_SCORES[robot], 0)
      

def CreateFakeQuarterFinalScores():
  CreateFakeScoreForMatches(21 - 4, 21)
  
def CreateFakeSemiFinalScores():
  CreateFakeScoreForMatches(23 - 2, 23)
  
def CreateFakeFinalsScores():
  CreateFakeScoreForMatches(24 - 1 , 24)

if __name__ == "__main__":
  if r.llen("org.srobo.matches") == 0:
    schedule_finals.AppendToMatches(SCHEDULED_MATCHES)
    print "Done adding match test data."
    
    CreateFakeResults()
    print "Done making fake results for league matches"
  elif r.llen("org.srobo.matches") == 21:
    # generate fake scores for the quarter-finals
    CreateFakeQuarterFinalScores()
    print "Done making fake results for the quarter finals"    
  elif r.llen("org.srobo.matches") == 23:
    # generate fake scores for the semi-finals
    CreateFakeSemiFinalScores()
    print "Done making fake results for the semi finals"
  else:
    # generate fake scores for the final
    CreateFakeFinalsScores()
    print "Done making fake results for the final" 
  
