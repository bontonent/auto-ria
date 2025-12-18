def get_agent(base_dir):
    with open("/".join([str(base_dir),'user_agents.txt'])) as f:
        lines = f.readlines()
        for i,line in enumerate(lines):
            lines[i] = line.replace('\n','').split('|')[-1].strip()
    return lines

# Example how use
if __name__ =='__main__':
    data = get_agent()
    print(data)