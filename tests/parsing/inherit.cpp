#include "catch.hpp"

#include "SystemCClang.h"
// This is automatically generated from cmake.
#include <iostream>
#include "ClangArgs.h"
#include "Testing.h"

using namespace systemc_clang;

// Source:
// https://www.toptip.ca/2010/03/trim-leading-or-trailing-white-spaces.html
std::string &trim(std::string &s) {
  size_t p = s.find_first_not_of(" \t");
  s.erase(0, p);

  p = s.find_last_not_of(" \t");
  if (string::npos != p) s.erase(p + 1);

  return s;
}

TEST_CASE("Basic inheritance check", "[inheritance]") {

  std::string code{systemc_clang::read_systemc_file(
      systemc_clang::test_data_dir, "inherit-input.cpp")};

  ASTUnit *from_ast =
      tooling::buildASTFromCodeWithArgs(code, systemc_clang::catch_test_args)
          .release();

  /// Turn debug on
  //
  llvm::DebugFlag = true;
  // llvm::setCurrentDebugType("SensitivityMatcher");

  SystemCConsumer systemc_clang_consumer{from_ast};
  systemc_clang_consumer.HandleTranslationUnit(from_ast->getASTContext());

  auto model{systemc_clang_consumer.getSystemCModel()};

  // This provides the module declarations.
  auto instances{model->getInstances()};

  // Want to find an instance named "testing".

  ModuleInstance *nested_module{model->getInstance("NestedModule")};
  ModuleInstance *test_module{model->getInstance("testing")};
  ModuleInstance *dut{model->getInstance("d")};

  SECTION("Found sc_module instances", "[instances]") {
    // There should be 2 modules identified.
    INFO("Checking number of sc_module instances found: " << instances.size());

    REQUIRE(instances.size() == 3);

    /// Ensure that all the modules are found.
    auto all_modules {( (nested_module != nullptr) && (test_module != nullptr) && (dut  != nullptr))};
    REQUIRE( all_modules );

    REQUIRE(test_module != nullptr);

    INFO("Checking member ports for NestedModule instance.");
    REQUIRE(nested_module->getIPorts().size() == 1);
    REQUIRE(nested_module->getOPorts().size() == 0);
    REQUIRE(nested_module->getIOPorts().size() == 0);
    REQUIRE(nested_module->getSignals().size() == 0);
    REQUIRE(nested_module->getInputStreamPorts().size() == 0);
    REQUIRE(nested_module->getOutputStreamPorts().size() == 0);
    REQUIRE(nested_module->getOtherVars().size() == 0);
    REQUIRE(nested_module->getNestedModuleInstances().size() == 0);



    INFO("Checking member ports for test instance.");
    // These checks should be performed on the declarations.

    // The module instances have all the information.
    // This is necessary until the parsing code is restructured.
    // There is only one module instance
    // auto module_instances{model->getModuleInstanceMap()};
    // auto p_module{module_decl.find("test")};
    //
    //
    auto test_module_inst{test_module};

    // Check if the proper number of ports are found.
    REQUIRE(test_module_inst->getIPorts().size() == 1);
    REQUIRE(test_module_inst->getOPorts().size() == 1);
    REQUIRE(test_module_inst->getIOPorts().size() == 0);
    REQUIRE(test_module_inst->getSignals().size() == 1);
    REQUIRE(test_module_inst->getInputStreamPorts().size() == 0);
    REQUIRE(test_module_inst->getOutputStreamPorts().size() == 0);
    REQUIRE(test_module_inst->getOtherVars().size() == 0);

    /// This one comes from the base class.
    REQUIRE(test_module_inst->getNestedModuleInstances().size() == 1);

    /// Check how many base classes it really has.
    REQUIRE(test_module_inst->getBaseInstances().size() == 1);
    auto base_decl{ test_module_inst->getBaseInstances().front()};
    REQUIRE(base_decl->getModuleClassDecl()->getNameAsString() == "Base");

    // Check process information
    //

    // processMapType
    auto process_map{test_module_inst->getProcessMap()};
    REQUIRE(process_map.size() == 1);

    for (auto const &proc : process_map) {
      auto entry_func{proc.second->getEntryFunction()};
      if (entry_func) {
        auto sense_map{entry_func->getSenseMap()};
        REQUIRE(sense_map.size() == 1);

        int check{1};
        for (auto const &sense : sense_map) {
          llvm::outs() << "@@@@@@@@@@@@@@@@@@************************* : "
                       << sense.first << "\n";
          if ((sense.first == "entry_function_1_handle__clkpos")) {
            --check;
          }
        }
        REQUIRE(check == 0);
      }
    }

    //
    // Check port types
    //
    //
    for (auto const &port : test_module_inst->getIPorts()) {
      std::string name{get<0>(port)};
      PortDecl *pd{get<1>(port)};
      FindTemplateTypes *template_type{pd->getTemplateType()};
      Tree<TemplateType> *template_args{template_type->getTemplateArgTreePtr()};

      // Print out each argument individually using the iterators.
      // Note: template_args must be dereferenced.
      for (auto const &node : *template_args) {
        const TemplateType *type_data{node->getDataPtr()};
        llvm::outs() << "\n- name: " << name
                     << ", type name: " << type_data->getTypeName() << " ";

        // Access the parent of the current node.
        // If the node is a pointer to itself, then the node itself is the
        // parent. Otherwise, it points to the parent node.
        auto parent_node{node->getParent()};
        if (parent_node == node) {
          llvm::outs() << "\n@> parent (itself) type name: "
                       << parent_node->getDataPtr()->getTypeName() << "\n";
        } else {
          // It is a different parent.
          llvm::outs() << "\n@> parent (different) type name: "
                       << parent_node->getDataPtr()->getTypeName() << "\n";
        }

        // Access the children for each parent.
        // We use the template_args to access it.

        auto children{template_args->getChildren(parent_node)};
        for (auto const &kid : children) {
          llvm::outs() << "@> child type name: "
                       << kid->getDataPtr()->getTypeName() << "\n";
        }
      }
      llvm::outs() << "\n";

      std::string dft_str{template_args->dft()};

      if (name == "clk") {
        REQUIRE(trim(dft_str) == "sc_in _Bool");
      }
      if ((name == "in1") || (name == "in2")) {
        REQUIRE(trim(dft_str) == "sc_in int");
      }
    }

    for (auto const &port : test_module_inst->getOPorts()) {
      auto name{get<0>(port)};
      PortDecl *pd{get<1>(port)};
      auto template_type{pd->getTemplateType()};
      auto template_args{template_type->getTemplateArgTreePtr()};

      std::string dft_str{template_args->dft()};

      if ((name == "out1") || (name == "out2")) {
        REQUIRE(trim(dft_str) == "sc_out int");
      }

    }

    for (auto const &sig : test_module_inst->getSignals()) {
      auto name{get<0>(sig)};
      SignalDecl *sg{get<1>(sig)};
      auto template_type{sg->getTemplateTypes()};
      auto template_args{template_type->getTemplateArgTreePtr()};

      // Get the tree as a string and check if it is correct.
      std::string dft_str{template_args->dft()};
      if (name == "internal_signal") {
        REQUIRE(trim(dft_str) == "sc_signal int");
      }

    }

    // Check netlist
    //
    //

    /// Port bindings
    //
    // Instance: testing
    REQUIRE(test_module->getPortBindings().size() == 0);

    // Instance: d
    auto port_bindings{dut->getPortBindings()};

    int check_count{2};
    for (auto const &binding : port_bindings) {
      PortBinding *pb{binding.second};
      std::string port_name{pb->getCallerPortName()};
      std::string caller_name{pb->getCallerInstanceName()};
      std::string as_string{pb->toString()};
      llvm::outs() << "check string: " << as_string << "\n";
      if (caller_name == "test_instance") {
        if (port_name == "in1") {
          REQUIRE(as_string == "test test_instance testing in1 sig1");
          --check_count;
        }
        if (port_name == "out1") {
          REQUIRE(as_string == "test test_instance testing out1 sig1");
          --check_count;
        }
      }
    }
    REQUIRE(check_count == 0);
  }
}
