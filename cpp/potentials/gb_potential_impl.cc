#include "gb_potential_impl.h"

#include <math.h>
#include <iostream>
#include <string>
#include <sstream>

using std::cout;
using std::endl;
using std::string;
using std::stringstream;
using std::vector;

namespace {

string toString(const vector<double>& v) {
    stringstream ss;
    ss << "(";
    for (int i = 0; i < v.size(); ++i) {
        ss << v[i];
        if (i < v.size() - 1) {
            ss << ", ";
        }
    }
    ss << ")";
    return ss.str();
}

vector<double> add(const vector<double>& v1, const vector<double>& v2) {
    vector<double> res(v1.size());
    for (int i = 0; i < v1.size(); ++i) {
        res[i] = v1[i] + v2[i];
    }
    //cout << "// " << toString(v1) << " + " << toString(v2) << " = " << toString(res) << endl;
    return res;
}

vector<double> sub(const vector<double>& v1, const vector<double>& v2) {
    vector<double> res(v1.size());
    for (int i = 0; i < v1.size(); ++i) {
        res[i] = v1[i] - v2[i];
    }
    //cout << "// " << toString(v1) << " - " << toString(v2) << " = " << toString(res) << endl;
    return res;
}

double dot(const vector<double>& v1, const vector<double>& v2) {
    double dot_product = 0.0;
    for (int i = 0; i < v1.size() ; ++i) {
        dot_product += v1[i] * v2[i];
    }
    //cout << "// " << toString(v1) << " . " << toString(v2) << " = " << dot_product << endl;
    return dot_product;
}

double norm(const vector<double>& v) {
    return sqrt(dot(v, v));
}

vector<double> normalize(const vector<double>& v) {
    vector<double> res(v);
    double n = norm(v);
    for (int i = 0; i < v.size(); ++i) {
        res[i] /= n;
    }
    return res;
}

}

GayBernesPotentialImpl::GayBernesPotentialImpl(
        double epsilon0, double sigma_s, double miu, double ni,
        double kappa, double kappa_tag)
    : epsilon0_(epsilon0), sigma_s_(sigma_s), miu_(miu), ni_(ni),
      kappa_(kappa), chi_(0.0), kappa_tag_(kappa_tag), chi_tag_(0.0) {
    double kappa_2 = kappa_ * kappa_;
    chi_ = (kappa_2 - 1.0) / (kappa_2 + 1.0);

    double kappa_tag_power = pow(kappa_tag_, 1.0 / miu_);
    chi_tag_ = (kappa_tag_power - 1.0) / (kappa_tag_power + 1.0);
    //cout << "// ^^^ GayBernesPotentialImpl: epsilon0_ = " << epsilon0_ << ", sigma_s_ = " << sigma_s_ << ", miu_ = " << miu_ << ", ni_ = " << ni_ << ", kapp_ = " << kappa_ << ", chi_ = " << chi_ << ", kappa_tag_ = " << kappa_tag_ << ", chi_tag_ = " << chi_tag_ << endl;
}

double GayBernesPotentialImpl::calculateTwoSpins(
        const vector<double>& spin1,
        const vector<double>& location1,
        const vector<double>& spin2,
        const vector<double>& location2) const {
    vector<double> r = sub(location1, location2);
    vector<double> nr = normalize(r);
    double U = calculateGBPotential(spin1, spin2, r, nr);
    //cout << "// GayBernesPotentialImpl::calculateTwoSpins:" << endl;
    //cout << "// spin1 = " << toString(spin1) << ", location1 = " << toString(location1) << endl;
    //cout << "// spin2 = " << toString(spin2) << ", location2 = " << toString(location2) << endl;
    //cout << "// r = " << toString(r) << ", nr = " << toString(nr) << endl;
    //cout << "// U = " << U << endl;
    return U;
}

double GayBernesPotentialImpl::calculateGBPotential(
        const vector<double>& spin1,
        const vector<double>& spin2,
        const vector<double>& r,
        const vector<double>& nr) const {
    double R = calculateR(spin1, spin2, r, nr);
    double epsilon = calculateEpsilon(spin1, spin2, nr);
    return (4 * epsilon * (pow(R, 12) - pow(R, 6)));
}

double GayBernesPotentialImpl::calculateR(
        const vector<double>& spin1,
        const vector<double>& spin2,
        const vector<double>& r,
        const vector<double>& nr) const {
    double sigma = calculateSigma(spin1, spin2, nr);
    return (sigma_s_ / (norm(r) - sigma + sigma_s_));
}

double GayBernesPotentialImpl::calculateSigma(
        const vector<double>& spin1,
        const vector<double>& spin2,
        const vector<double>& nr) const {
    double first  = pow(dot(spin1, nr) + dot(spin2, nr), 2) /
                   (1.0 + chi_ * dot(spin1, spin2));
    double second = pow(dot(spin1, nr) - dot(spin2, nr), 2) /
                   (1.0 - chi_ * dot(spin1, spin2));
    return sigma_s_ / sqrt(1.0 - chi_ / 2.0 * (first + second));
}

double GayBernesPotentialImpl::calculateEpsilon(
        const vector<double>& spin1,
        const vector<double>& spin2,
        const vector<double>& nr) const {
    return (epsilon0_ *
            pow(calculateEpsilonNi(spin1, spin2), ni_) *
            pow(calculateEpsilonTagMiu(spin1, spin2, nr), miu_));
}

double GayBernesPotentialImpl::calculateEpsilonNi(
        const vector<double>& spin1,
        const vector<double>& spin2) const {
    return 1.0 / sqrt(1.0 - (chi_ * chi_) * pow(dot(spin1, spin2), 2));
}

double GayBernesPotentialImpl::calculateEpsilonTagMiu(
        const vector<double>& spin1,
        const vector<double>& spin2,
        const vector<double>& nr) const {
    double first  = pow(dot(spin1, nr) + dot(spin2, nr), 2) /
                   (1.0 + chi_tag_ * dot(spin1, spin2));
    double second = pow(dot(spin1, nr) - dot(spin2, nr), 2) /
                   (1.0 - chi_tag_ * dot(spin1, spin2));
    return 1.0 - chi_tag_ / 2.0 * (first + second);
}
