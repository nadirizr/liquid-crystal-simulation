%module gb_potential_impl
%{ 
    #define SWIG_FILE_WITH_INIT
    #include "gb_potential_impl.h"
%}

%include "std_vector.i"
namespace std {
    %template(DoubleVector) vector<double>;
}

%include "gb_potential_impl.h"
