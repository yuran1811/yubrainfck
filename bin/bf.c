/* The world's smallest Brainfuck interpreter in C, by Kang Seonghoon (160 bytes)
 * http://j.mearie.org/post/1181041789/brainfuck-interpreter-in-2-lines-of-c */
s[99],*r=s,*d,c;main(a,b){char*v=1[d=b];for(;c=*v++%93;)for(b=c&2,b=c%7?a&&(c&17
?c&1?(*r+=b-1):(r+=b-1):syscall(4-!b,b,r,1),0):v;b&&c|a**r;v=d)main(!c,&a);d=v;}