def f(n, a=4, b=3, c=2):
    print('n: {}, a: {}, b: {}, c: {}'.format(n,a,b,c))


l = {
    'n': 19,
    'a': 13,
    'b': 16,
    'c': 18
}
f(**l)
