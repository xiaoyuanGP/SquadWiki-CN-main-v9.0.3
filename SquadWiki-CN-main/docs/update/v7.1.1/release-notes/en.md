# SQUAD HOTFIX 7.1.1 RELEASE NOTES

> 页面贡献者：Offworld Industries
> 
> 原文章：[SQUAD HOTFIX 7.1 RELEASE NOTES](https://www.joinsquad.com/updates/squad-7-1-RELEASE-NOTES)
>
> 发布时间：2023/3/14

## SYSTEM & GAMEPLAY UPDATES
GENERAL BUG FIXES
Added direct server pinging to the server browser. The initial server browser search will still work using a region ping filter. After that, the returned servers will be individually pinged. This should make the server ping shown in the server browser more accurate.
Fixed no servers being shown in the server browser when opening it quickly or after disconnecting from a server
Fixed the “Favorites” server tab showing all servers. It will now correctly only show favorite servers
Fixed the “Recents” server tab showing all servers. It will now correctly only show recent servers
Fixed previous results being returned when no results are found in a server browser search. It will now correctly return no results if there are no results.
Fixed a client crash that occurred when going into admin cam at the start of a match
Sanxian Islands: fixed a wall on Power Plant being too thin, allowing players to look through it
Sanxian Islands: fixed a wall on Power Plant having no collision, allowing players to walk through it
Sanxian Islands: fixed a Power Plant ceiling that allowed players to vault into it
Sanxian RAAS v2: fixed ADF main base RHIBs being outside of the resupply radius
Sanxian Invasion v1: fixed USMC UH-1Y helicopter spawning at 50% health
Sanxian AAS v2: fixed an ammo crate being on top of a helipad
KNOWN ISSUES
If server browser filters are too broad (for example, filtering at 500 ping), the number of results returned will be truncated to 200. As a result, you may not see all servers. To remedy this, we recommend using a sufficiently low (200 or less) ping filter.
Tag filtering currently happens on the client after the server results are returned. This means filtering by tags (such as language) will not work as a workaround for hitting the 200 results cap mentioned above. For now, ping filtering is the most reliable way to circumvent that. Moving tag filtering to happen during the search query itself is being worked on for a future update.
The filtering of servers is still done using region ping. This means there may be a discrepancy in server browser results if a server has a much lower or higher region ping than their direct server ping for some reason.