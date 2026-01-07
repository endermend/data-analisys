--Needed experience to gain level
SELECT level+1 as level, CONVERT (SUM(lvlup_exp) OVER (ORDER BY level ASC), UNSIGNED) as "Needed EXP" FROM Levels

--Top players by experience
SELECT p.id, p.name AS NAME, p.exp+Lvls.exp AS EXP FROM Players p
LEFT JOIN (
    SELECT 1 AS level, 0 AS exp
    UNION
    SELECT level+1 AS level, SUM(lvlup_exp) OVER (ORDER BY level ASC) AS exp FROM Levels
) Lvls ON p.level = Lvls.level
ORDER BY EXP DESC
LIMIT 3

--Top events
SELECT id, name, repeats FROM (SELECT event, SUM(repeats) as repeats FROM PlayerEvents GROUP BY event ORDER BY event) as que
LEFT JOIN Events ON Events.id = que.event
ORDER BY repeats DESC

--Total players
SELECT count(*) FROM Players

--Total events
SELECT count(*) FROM PlayerEvents