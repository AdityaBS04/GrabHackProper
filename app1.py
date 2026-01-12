def dfs1(lis):
    adj = defaultdict(list)
    for i,j in lis:
        adj[i].append(j)
        adj[j].append(i)
    visited = [False]*len(adj)
    def dfs(node,visited):
        visited[node] = True
        for i in adj[node]:
            if i not in visited:
                dfs(i,visited)
    for i in range(len(adj)):
        if not visited[i]:
            dfs(i,visited)
            count += 1
    return count
