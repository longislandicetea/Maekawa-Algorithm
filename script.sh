kill `lsof -i:3000`
kill `lsof -i:3001`
kill `lsof -i:3002`
kill `lsof -i:3003`
kill `lsof -i:3004`
kill `lsof -i:3005`
kill `lsof -i:3006`
kill `lsof -i:3007`
kill `lsof -i:3008`

python mutex.py -cs_int 5 -next_req 7 -tot_exec_time 10 -option 1