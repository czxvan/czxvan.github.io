#include<iostream>
using namespace std;

void func1(int a) {
	cout << a << endl;
}

void func2(int& a) {
	cout << a << endl;
}


int main() {
	cout << "hello C++" << endl;
	int a = 10;
	func1(a);

	func2(a);
	
	return 0;
}