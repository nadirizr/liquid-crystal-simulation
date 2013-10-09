#ifndef _GAY_BERNES_POTENTIAL_IMPL_H_
#define _GAY_BERNES_POTENTIAL_IMPL_H_

#include <vector>

class GayBernesPotentialImpl {
  public:
    GayBernesPotentialImpl(double epsilon0, double sigma_s, double miu, double ni,
                           double kappa, double kappa_tag);

    double calculateTwoSpins(const std::vector<double>& spin1,
                            const std::vector<double>& location1,
                            const std::vector<double>& spin2,
                            const std::vector<double>& location2) const;

  private:
    double calculateGBPotential(double dot_spin1_nr,
                                double dot_spin2_nr,
                                double dot_spin1_spin2,
                                double n) const;

    double calculateR(double dot_spin1_nr,
                      double dot_spin2_nr,
                      double dot_spin1_spin2,
                      double n) const;

    double calculateSigma(double dot_spin1_nr,
                          double dot_spin2_nr,
                          double dot_spin1_spin2) const;

    double calculateEpsilon(double dot_spin1_nr,
                            double dot_spin2_nr,
                            double dot_spin1_spin2) const;

    double calculateEpsilonNi(double dot_spin1_spin2) const;

    double calculateEpsilonTagMiu(double dot_spin1_nr,
                                  double dot_spin2_nr,
                                  double dot_spin1_spin2) const;

    double epsilon0_;
    double sigma_s_;
    double miu_;
    double ni_;
    double kappa_;
    double chi_;
    double kappa_tag_;
    double chi_tag_;
};

#endif
