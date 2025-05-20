import { Navigation } from '../components/Navigation';
import Link from 'next/link';
import { 
  Shield, 
  BarChart as Chart, 
  Clock, 
  Award, 
  Users, 
  FileText,
  Building,
  ArrowRight,
  Check,
  Globe
} from 'lucide-react';

export default function Home() {
  const testimonials = [
    {
      quote: "Transformed our screening process and improved patient outcomes by 45%",
      author: "Dr. Sarah Chen",
      role: "Chief of Ophthalmology",
      organization: "Metropolitan Health"
    },
    {
      quote: "The accuracy and speed of detection has revolutionized our workflow",
      author: "Dr. James Wilson",
      role: "Medical Director",
      organization: "Healthcare Partners"
    }
  ];

  const stats = [
    { value: "99.2%", label: "Detection Accuracy" },
    { value: "500k+", label: "Images Analyzed" },
    { value: "85%", label: "Time Saved" },
    { value: "200+", label: "Healthcare Partners" }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white">
      <Navigation />
      
      {/* Hero Section with Animation */}
      <main className="max-w-7xl mx-auto py-16 px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <div className="inline-block mb-4 px-4 py-2 bg-blue-50 rounded-full">
            <span className="text-blue-600 font-semibold">FDA Approved Technology</span>
          </div>
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl md:text-6xl mb-6">
            <span className="text-blue-600">AI-Powered</span> Diabetic{' '}
            <span className="block">Retinopathy Detection</span>
          </h1>
          <p className="mt-3 max-w-md mx-auto text-xl text-gray-600 sm:max-w-3xl">
            Enterprise-grade retinal analysis platform that delivers unprecedented accuracy
            and efficiency in diabetic retinopathy screening.
          </p>
          
          {/* CTA Buttons */}
          <div className="mt-8 flex justify-center gap-4">
            <Link href="/demo" className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg text-white bg-blue-600 hover:bg-blue-700 transition-colors duration-150">
              Schedule Demo
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
            <Link href="/contact" className="inline-flex items-center px-8 py-4 border-2 border-blue-600 text-lg font-medium rounded-lg text-blue-600 bg-white hover:bg-blue-50 transition-colors duration-150">
              Contact Sales
            </Link>
          </div>
        </div>

        {/* Stats Section */}
        <div className="mt-20 bg-white rounded-xl shadow-xl p-8">
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <div key={index} className="text-center">
                <div className="text-4xl font-bold text-blue-600">{stat.value}</div>
                <div className="mt-2 text-gray-600">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        {/* Key Benefits with Enhanced Visual Design */}
        <div className="mt-24">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-4">
            Enterprise Benefits
          </h2>
          <p className="text-xl text-gray-600 text-center mb-12 max-w-3xl mx-auto">
            Our platform delivers comprehensive solutions for healthcare organizations
            of all sizes.
          </p>
          <div className="grid gap-8 md:grid-cols-3">
            {[
              {
                icon: <Chart className="w-8 h-8 text-blue-600" />,
                title: "Unmatched Accuracy",
                description: "99.2% accuracy rate with clinically validated results across diverse patient populations."
              },
              {
                icon: <Clock className="w-8 h-8 text-blue-600" />,
                title: "Lightning-Fast Analysis",
                description: "Process over 500 images per hour with real-time results and instant reporting."
              },
              {
                icon: <Shield className="w-8 h-8 text-blue-600" />,
                title: "Enterprise Security",
                description: "HIPAA-compliant infrastructure with end-to-end encryption and audit logging."
              }
            ].map((benefit, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-8 hover:shadow-xl transition-shadow duration-300">
                <div className="flex items-center justify-center w-16 h-16 bg-blue-50 rounded-lg mb-6 mx-auto">
                  {benefit.icon}
                </div>
                <h3 className="text-xl font-semibold text-center mb-4">{benefit.title}</h3>
                <p className="text-gray-600 text-center">{benefit.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Testimonials Section */}
        <div className="mt-24 bg-blue-600 rounded-2xl p-8 md:p-12">
          <h2 className="text-3xl font-bold text-white text-center mb-12">
            Trusted by Leading Healthcare Providers
          </h2>
          <div className="grid md:grid-cols-2 gap-8">
            {testimonials.map((testimonial, index) => (
              <div key={index} className="bg-white rounded-lg p-6 shadow-lg">
                <p className="text-lg text-gray-600 mb-4">&ldquo;{testimonial.quote}&rdquo;</p>
                <div className="flex items-center">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <span className="text-blue-600 font-bold">
                      {testimonial.author[0]}
                    </span>
                  </div>
                  <div className="ml-4">
                    <p className="font-semibold text-gray-900">{testimonial.author}</p>
                    <p className="text-gray-600">{testimonial.role}</p>
                    <p className="text-gray-500">{testimonial.organization}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Features Grid with Enhanced Design */}
        <div className="mt-24">
          <h2 className="text-3xl font-extrabold text-gray-900 text-center mb-12">
            Enterprise-Grade Features
          </h2>
          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
            {[
              {
                icon: <Users className="w-6 h-6 text-blue-600" />,
                title: "Team Collaboration",
                description: "Role-based access control with custom workflows and team permissions."
              },
              {
                icon: <FileText className="w-6 h-6 text-blue-600" />,
                title: "Advanced Analytics",
                description: "Real-time dashboards with customizable reports and data visualization."
              },
              {
                icon: <Award className="w-6 h-6 text-blue-600" />,
                title: "Seamless Integration",
                description: "REST API and HL7 FHIR support for healthcare system integration."
              },
              {
                icon: <Globe className="w-6 h-6 text-blue-600" />,
                title: "Global Accessibility",
                description: "Cloud-based platform accessible from anywhere with proper credentials."
              },
              {
                icon: <Building className="w-6 h-6 text-blue-600" />,
                title: "Enterprise Support",
                description: "24/7 dedicated support with guaranteed response times."
              },
              {
                icon: <Check className="w-6 h-6 text-blue-600" />,
                title: "Compliance Ready",
                description: "Built-in compliance tools for HIPAA, GDPR, and SOC 2."
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
                <div className="flex items-center mb-4">
                  <div className="w-12 h-12 bg-blue-50 rounded-lg flex items-center justify-center">
                    {feature.icon}
                  </div>
                  <h3 className="text-lg font-semibold ml-4">{feature.title}</h3>
                </div>
                <p className="text-gray-600">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Final CTA Section */}
        <div className="mt-24 text-center bg-gradient-to-r from-blue-600 to-blue-800 rounded-2xl p-12">
          <h2 className="text-3xl font-bold text-white mb-6">
            Ready to Transform Your Screening Process?
          </h2>
          <p className="text-xl text-blue-100 mb-8 max-w-2xl mx-auto">
            Join leading healthcare providers in revolutionizing diabetic retinopathy detection.
          </p>
          <div className="flex justify-center gap-4">
            <Link href="/demo" className="inline-flex items-center px-8 py-4 bg-white text-blue-600 rounded-lg font-medium hover:bg-blue-50 transition-colors duration-150">
              Schedule Demo
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}