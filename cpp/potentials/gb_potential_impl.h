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
    double calculateGBPotential(const std::vector<double>& spin1,
                               const std::vector<double>& spin2,
                               const std::vector<double>& r,
                               const std::vector<double>& nr) const;

    double calculateR(const std::vector<double>& spin1,
                     const std::vector<double>& spin2,
                     const std::vector<double>& r,
                     const std::vector<double>& nr) const;

    double calculateSigma(const std::vector<double>& spin1,
                         const std::vector<double>& spin2,
                         const std::vector<double>& nr) const;

    double calculateEpsilon(const std::vector<double>& spin1,
                           const std::vector<double>& spin2,
                           const std::vector<double>& nr) const;

    double calculateEpsilonNi(const std::vector<double>& spin1,
                             const std::vector<double>& spin2) const;

    double calculateEpsilonTagMiu(const std::vector<double>& spin1,
                                 const std::vector<double>& spin2,
                                 const std::vector<double>& nr) const;

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
